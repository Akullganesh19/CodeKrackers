import time
import functools
import logging
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger("vas.resilience")

T = TypeVar('T')

class CircuitBreakerOpenException(Exception):
    pass

def with_retries(max_attempts: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Final error: {e}")
                        raise
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            now = time.time()
            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state.")
                    self.state = "HALF_OPEN"
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Rejecting call.")
                    raise CircuitBreakerOpenException(f"Circuit breaker is open for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    logger.info(f"Circuit breaker for {func.__name__} closing after successful call.")
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    logger.error(f"Circuit breaker for {func.__name__} opening after {self.failures} failures. Last error: {e}")
                    self.state = "OPEN"
                raise

        return wrapper

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    """
    Circuit breaker decorator factory.
    """
    return CircuitBreaker(failure_threshold, recovery_timeout)
