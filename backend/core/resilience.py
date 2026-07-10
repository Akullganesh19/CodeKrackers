import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Optional, Tuple, Type, Union

logger = logging.getLogger("vas.resilience")


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,  # noqa: E501
):
    """
    Decorator for retrying async or sync functions with exponential backoff.
    """

    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                attempt = 1
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt >= max_attempts:
                            logger.error(
                                f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}"  # noqa: E501
                            )
                            raise e
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)  # noqa: E501
                        logger.warning(
                            f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s..."  # noqa: E501
                        )
                        await asyncio.sleep(delay)
                        attempt += 1

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                attempt = 1
                while True:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt >= max_attempts:
                            logger.error(
                                f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}"  # noqa: E501
                            )
                            raise e
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)  # noqa: E501
                        logger.warning(
                            f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s..."  # noqa: E501
                        )
                        time.sleep(delay)
                        attempt += 1

            return sync_wrapper

    return decorator


class CircuitBreaker:
    """
    Stateful circuit breaker to prevent cascading failures.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):  # noqa: E501
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = (
            "CLOSED"  # CLOSED, OPEN, HALF_OPEN  # noqa: E501
        )

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            if self.state != "OPEN":
                logger.error(
                    f"Circuit Breaker OPENED after {self.failure_count} failures."  # noqa: E501
                )
            self.state = "OPEN"

    def record_success(self):
        if self.state != "CLOSED":
            logger.info("Circuit Breaker CLOSED (recovery successful).")
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker HALF_OPEN (testing recovery).")
                return True
            return False
        # HALF_OPEN - allow one execution to test
        return True


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    fallback_func: Optional[Callable] = None,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,  # noqa: E501
):
    """
    Decorator for circuit breaking.
    """
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not breaker.can_execute():
                    if fallback_func:
                        logger.warning(
                            f"Circuit OPEN for {func.__name__}, calling fallback."  # noqa: E501
                        )
                        if asyncio.iscoroutinefunction(fallback_func):
                            return await fallback_func(*args, **kwargs)
                        return fallback_func(*args, **kwargs)
                    raise Exception(f"Circuit breaker OPEN for {func.__name__}")  # noqa: E501
                try:
                    result = await func(*args, **kwargs)
                    breaker.record_success()
                    return result
                except exceptions as e:
                    breaker.record_failure()
                    if fallback_func:
                        if asyncio.iscoroutinefunction(fallback_func):
                            return await fallback_func(*args, **kwargs)
                        return fallback_func(*args, **kwargs)
                    raise e

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not breaker.can_execute():
                    if fallback_func:
                        logger.warning(
                            f"Circuit OPEN for {func.__name__}, calling fallback."  # noqa: E501
                        )
                        return fallback_func(*args, **kwargs)
                    raise Exception(f"Circuit breaker OPEN for {func.__name__}")  # noqa: E501
                try:
                    result = func(*args, **kwargs)
                    breaker.record_success()
                    return result
                except exceptions as e:
                    breaker.record_failure()
                    if fallback_func:
                        return fallback_func(*args, **kwargs)
                    raise e

            return sync_wrapper

    return decorator
