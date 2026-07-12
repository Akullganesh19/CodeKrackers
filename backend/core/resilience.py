import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger("vas.resilience")

R = TypeVar("R")

def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(f"Failed after {max_attempts} attempts: {func.__name__} - {e}")
                            raise e

                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {delay}s")
                        await asyncio.sleep(delay)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(f"Failed after {max_attempts} attempts: {func.__name__} - {e}")
                            raise e

                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {delay}s")
                        time.sleep(delay)
            return sync_wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit breaker moved to HALF-OPEN state")

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("Circuit breaker moved to CLOSED state")
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker tripped OPEN after {self.failures} failures")

    def __call__(self, func: Callable[..., R]) -> Callable[..., R]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> R:
                self._check_state()

                if self.state == "OPEN":
                    raise Exception("Circuit breaker is OPEN")

                try:
                    result = await func(*args, **kwargs)
                    self.record_success()
                    return result
                except Exception as e:
                    self.record_failure()
                    raise e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> R:
                self._check_state()

                if self.state == "OPEN":
                    raise Exception("Circuit breaker is OPEN")

                try:
                    result = func(*args, **kwargs)
                    self.record_success()
                    return result
                except Exception as e:
                    self.record_failure()
                    raise e
            return sync_wrapper

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0) -> Callable:
    cb = CircuitBreaker(failure_threshold, recovery_timeout)
    return cb
