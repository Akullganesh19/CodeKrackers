import time
import logging
from functools import wraps
from enum import Enum

logger = logging.getLogger("vas.resilience")

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"CircuitBreaker for {func.__name__} entering HALF_OPEN state.")
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure(func.__name__, e)
                raise

        return wrapper

    def _on_success(self):
        # Reset failure count to 0 on every successful request
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            logger.info("CircuitBreaker successfully recovered. State is now CLOSED.")
            self.state = CircuitState.CLOSED

    def _on_failure(self, func_name: str, exception: Exception):
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.last_failure_time = time.time()
            logger.warning(f"CircuitBreaker for {func_name} failed in HALF_OPEN state. Returning to OPEN.")
        else:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_failure_time = time.time()
                logger.error(f"CircuitBreaker for {func_name} tripped to OPEN state after {self.failure_count} failures.")

def with_retry_sync(max_attempts: int = 3, initial_backoff: float = 0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after failure: {e}. Waiting {backoff}s.")
                    time.sleep(backoff)
                    attempt += 1
        return wrapper
    return decorator
