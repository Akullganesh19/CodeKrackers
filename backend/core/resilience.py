import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit HALF-OPEN for {func.__name__}")
                    self.state = "HALF-OPEN"
                else:
                    logger.warning(
                        f"Circuit OPEN for {func.__name__}. Fast-failing."
                    )
                    raise Exception(f"Circuit OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(f"Circuit CLOSED for {func.__name__}")
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    logger.error(
                        f"Circuit OPENED for {func.__name__} after "
                        f"{self.failure_count} failures"
                    )
                    self.state = "OPEN"
                raise e

        return wrapper

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: int = 30):
    return CircuitBreaker(failure_threshold, recovery_timeout)

def with_retries(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for "
                        f"{func.__name__} after {delay}s: {e}"
                    )
                    time.sleep(delay)
        return wrapper
    return decorator
