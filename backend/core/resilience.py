import time
import logging
from functools import wraps
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

class CircuitState(Enum):
    CLOSED = "CLOSED"     # Normal operation, requests flow freely
    OPEN = "OPEN"         # Circuit is broken, requests fail immediately
    HALF_OPEN = "HALF_OPEN" # Testing if the underlying service has recovered

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 60, expected_exception: type = Exception):
        """
        State machine that trips on successive failures, allowing fast failure when dependencies are down,
        and periodically retrying after a cooldown.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(f"CircuitBreaker for {func.__name__} entering HALF_OPEN state")
                    self.state = CircuitState.HALF_OPEN
                else:
                    logger.warning(f"CircuitBreaker OPEN for {func.__name__} - failing fast")
                    raise CircuitBreakerOpenException(f"Circuit for {func.__name__} is OPEN")

            try:
                result = func(*args, **kwargs)

                # If we get here and we were HALF_OPEN, the service is recovered
                if self.state == CircuitState.HALF_OPEN:
                    logger.info(f"CircuitBreaker for {func.__name__} recovered, entering CLOSED state")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

                return result

            except self.expected_exception as e:
                # Record failure
                self.failure_count += 1
                self.last_failure_time = time.time()

                logger.warning(f"CircuitBreaker failure for {func.__name__} (count: {self.failure_count}): {e}")

                if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
                    if self.state != CircuitState.OPEN:
                        logger.error(f"CircuitBreaker TRIPPED for {func.__name__} - entering OPEN state")
                        self.state = CircuitState.OPEN

                raise

        return wrapper

def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, expected_exception: type = Exception):
    """
    Retry decorator with exponential backoff for synchronous functions.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except expected_exception as e:
                    if attempt >= max_attempts:
                        logger.error(f"Retry exhausted for {func.__name__} after {max_attempts} attempts. Last error: {e}")
                        raise

                    logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)

                    attempt += 1
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator
