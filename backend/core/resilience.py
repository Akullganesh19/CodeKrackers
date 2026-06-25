import asyncio
import functools
import logging
import time
from typing import Any, Callable, Tuple, Type, TypeVar

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")


class CircuitBreakerOpenException(Exception):
    pass


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """Auto-Retry with Exponential Backoff for synchronous functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Action '{func.__name__}' failed after {max_attempts} attempts. Error: {e}"
                        )
                        raise
                    logger.warning(
                        f"Action '{func.__name__}' failed on attempt {attempt}/{max_attempts}. Retrying in {delay}s. Error: {e}"
                    )
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            raise Exception("Unreachable")

        return wrapper

    return decorator


def async_with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """Auto-Retry with Exponential Backoff for asynchronous functions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Async action '{func.__name__}' failed after {max_attempts} attempts. Error: {e}"
                        )
                        raise
                    logger.warning(
                        f"Async action '{func.__name__}' failed on attempt {attempt}/{max_attempts}. Retrying in {delay}s. Error: {e}"
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            raise Exception("Unreachable")

        return wrapper

    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker OPENED after {self.failure_count} failures."
            )

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("Circuit breaker CLOSED. Service recovered.")
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker HALF_OPEN. Testing service recovery.")
                return True
            return False
        if self.state == "HALF_OPEN":
            return False  # Only allow one test request
        return True


def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    """Circuit Breaker for synchronous functions to prevent cascading failures."""
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not cb.can_execute():
                logger.error(
                    f"Circuit breaker is OPEN. Skipping execution of '{func.__name__}'."
                )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN for {func.__name__}"
                )

            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                raise

        return wrapper

    return decorator


def async_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    """Circuit Breaker for asynchronous functions to prevent cascading failures."""
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not cb.can_execute():
                logger.error(
                    f"Circuit breaker is OPEN. Skipping execution of '{func.__name__}'."
                )
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN for {func.__name__}"
                )

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                raise

        return wrapper

    return decorator
