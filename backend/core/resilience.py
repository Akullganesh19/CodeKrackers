import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")


def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.5) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Retry max attempts reached for {func.__name__}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Retry {attempt} for {func.__name__} after {delay}s due to {e}"
                    )
                    time.sleep(delay)
            return None

        return wrapper

    return decorator


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self, fallback: Callable = None, max_failures: int = 5, cooldown: float = 60.0
    ):
        self.fallback = fallback
        self.max_failures = max_failures
        self.cooldown = cooldown
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if self.state == "OPEN":
                if now - self.last_failure_time > self.cooldown:
                    self.state = "HALF_OPEN"
                    logger.info(f"Circuit for {func.__name__} is HALF_OPEN")
                else:
                    if self.fallback:
                        logger.warning(
                            f"Circuit for {func.__name__} is OPEN, returning fallback"
                        )
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(
                        f"Circuit OPEN for {func.__name__}"
                    )

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN" or self.state == "CLOSED":
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.max_failures:
                    self.state = "OPEN"
                    logger.error(f"Circuit for {func.__name__} OPENED due to {e}")
                if self.fallback:
                    return self.fallback(*args, **kwargs)
                raise e

        return wrapper
