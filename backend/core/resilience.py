import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar, Optional, cast

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")


def with_retry_sync(
    max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise e

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
            raise RuntimeError(
                f"Unexpected exit in with_retry_sync for {func.__name__}"
            )

        return wrapper

    return decorator


def with_retry_async(
    max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0
):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise e

                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s: {e}"
                    )
                    await asyncio.sleep(delay)
            raise RuntimeError(
                f"Unexpected exit in with_retry_async for {func.__name__}"
            )

        return wrapper

    return decorator


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 30.0,
        fallback: Optional[Callable] = None,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback

        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            now = time.time()

            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(
                        f"Circuit breaker for {func.__name__} entering HALF-OPEN state."
                    )
                    self.state = "HALF-OPEN"
                else:
                    if self.fallback:
                        logger.warning(
                            f"Circuit breaker OPEN for {func.__name__}. Executing fallback."
                        )
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker for {func.__name__} is OPEN"
                    )

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.state == "HALF-OPEN":
                    logger.error(
                        f"Circuit breaker for {func.__name__} tripped again in HALF-OPEN state: {e}"
                    )
                    self.state = "OPEN"
                elif self.failure_count >= self.failure_threshold:
                    logger.error(
                        f"Circuit breaker for {func.__name__} tripped. OPENING circuit: {e}"
                    )
                    self.state = "OPEN"

                if self.fallback:
                    logger.warning(
                        f"Executing fallback for {func.__name__} due to exception: {e}"
                    )
                    return self.fallback(*args, **kwargs)
                raise e
            else:
                if self.state == "HALF-OPEN":
                    logger.info(
                        f"Circuit breaker for {func.__name__} recovered. CLOSING circuit."
                    )
                self.failure_count = 0
                self.state = "CLOSED"
                return result

        return wrapper
