import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type

logger = logging.getLogger("vas.resilience")


def async_with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}"
                        )
                        raise
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                    delay = min(delay * 2, max_delay)

        return wrapper

    return decorator


def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}"
                        )
                        raise
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                    attempt += 1
                    delay = min(delay * 2, max_delay)

        return wrapper

    return decorator


class CircuitBreakerOpenError(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN.")

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


def async_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    fallback_func: Optional[Callable] = None,
):
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                cb.check_state()
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker OPEN for {func.__name__}")
                if fallback_func:
                    return (
                        await fallback_func(*args, **kwargs)
                        if asyncio.iscoroutinefunction(fallback_func)
                        else fallback_func(*args, **kwargs)
                    )
                raise e

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                logger.error(f"Circuit breaker failure for {func.__name__}. Error: {e}")
                if fallback_func and cb.state == "OPEN":
                    return (
                        await fallback_func(*args, **kwargs)
                        if asyncio.iscoroutinefunction(fallback_func)
                        else fallback_func(*args, **kwargs)
                    )
                raise

        return wrapper

    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    fallback_func: Optional[Callable] = None,
):
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                cb.check_state()
            except CircuitBreakerOpenError as e:
                logger.error(f"Circuit breaker OPEN for {func.__name__}")
                if fallback_func:
                    return fallback_func(*args, **kwargs)
                raise e

            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                logger.error(f"Circuit breaker failure for {func.__name__}. Error: {e}")
                if fallback_func and cb.state == "OPEN":
                    return fallback_func(*args, **kwargs)
                raise

        return wrapper

    return decorator
