import asyncio
import functools
import logging
import time
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

class CircuitOpenException(Exception):
    """Raised when the circuit breaker is open and requests are blocked."""
    pass

def with_retries(max_attempts: int = 3, initial_backoff_ms: int = 100):
    """
    Retries the wrapped function upon failure, using exponential backoff.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    sleep_time = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Function {func.__name__} attempt {attempt} failed, retrying in {sleep_time}s: {e}")
                    time.sleep(sleep_time)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    sleep_time = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Function {func.__name__} attempt {attempt} failed, retrying in {sleep_time}s: {e}")
                    await asyncio.sleep(sleep_time)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            if self.state != "OPEN":
                logger.error(f"CircuitBreaker OPENED after {self.failures} failures.")
            self.state = "OPEN"

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("CircuitBreaker CLOSED after success.")
        self.failures = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = "HALF-OPEN"
                return True
            return False
        if self.state == "HALF-OPEN":
            # Only allow one request to pass through in half-open state
            # If it succeeds, it closes. If it fails, it opens.
            return True
        return False


def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 30.0):
    """
    Circuit breaker decorator. If failures exceed the threshold, opens the circuit
    and raises CircuitOpenException without calling the function, until the recovery timeout passes.
    """
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not cb.can_execute():
                logger.warning(f"Circuit is OPEN. Blocked call to {func.__name__}.")
                raise CircuitOpenException(f"Circuit breaker open for {func.__name__}")
            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                raise e

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not cb.can_execute():
                logger.warning(f"Circuit is OPEN. Blocked call to {func.__name__}.")
                raise CircuitOpenException(f"Circuit breaker open for {func.__name__}")
            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                raise e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
