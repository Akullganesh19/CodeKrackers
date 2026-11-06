import functools
import time
import logging
from typing import Callable, Any, Optional

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    State machine for circuit breaking.
    States:
    - CLOSED: Normal operation. Passes through calls. If it fails `failure_threshold` times, transition to OPEN.
    - OPEN: Fails fast (or returns fallback). Waits `recovery_timeout` before transitioning to HALF-OPEN.
    - HALF-OPEN: Allows 1 call through. If success, transition to CLOSED. If fail, transition back to OPEN.
    """
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        fallback: Optional[Callable] = None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback

        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = 0.0

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"CircuitBreaker for {func.__name__} HALF_OPEN: Testing endpoint.")
            else:
                if self.fallback:
                    return self.fallback(*args, **kwargs)
                raise CircuitBreakerOpenException(f"Circuit for {func.__name__} is OPEN.")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(f"CircuitBreaker for {func.__name__} CLOSED: Service recovered.")
            elif self.state == "CLOSED":
                self.failures = 0 # Reset failures on success while closed!
            return result
        except Exception as e:
            if isinstance(e, CircuitBreakerOpenException):
                raise
            self.failures += 1
            self.last_failure_time = time.time()
            if self.state == "HALF_OPEN" or self.failures >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning(f"CircuitBreaker for {func.__name__} OPEN: Failed {self.failures} times. {str(e)}")
            raise

def with_retry_sync(max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """
    Retry decorator with exponential backoff for synchronous functions.
    DO NOT use on non-idempotent functions (e.g. sending SMS).
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"Retry {max_retries} failed for {func.__name__}: {str(e)}")
                        raise
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
