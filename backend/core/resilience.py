import asyncio
import logging
import time
from typing import Callable, Any, TypeVar, Awaitable, Optional

T = TypeVar('T')
logger = logging.getLogger('vas.resilience')

def with_retry_async(
    max_attempts: int = 3,
    base_delay_ms: int = 100,
    backoff_factor: float = 2.0
):
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        async def wrapper(*args, **kwargs):
            delay = base_delay_ms / 1000.0
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Final attempt {attempt} failed for {func.__name__}: {e}")
                        raise
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

def with_retry_sync(
    max_attempts: int = 3,
    base_delay_ms: int = 100,
    backoff_factor: float = 2.0
):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs):
            delay = base_delay_ms / 1000.0
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Final attempt {attempt} failed for {func.__name__}: {e}")
                        raise
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_secs: int = 30,
        fallback: Optional[Callable[..., Any]] = None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_secs = recovery_timeout_secs
        self.fallback = fallback

        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0

    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            current_time = time.time()

            if self.state == "OPEN":
                if current_time - self.last_failure_time > self.recovery_timeout_secs:
                    logger.info(f"Circuit for {func.__name__} HALF-OPEN, testing...")
                    self.state = "HALF-OPEN"
                else:
                    if self.fallback:
                        logger.warning(f"Circuit for {func.__name__} OPEN, using fallback")
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Circuit for {func.__name__} is OPEN")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN" or self.state == "CLOSED":
                    self.failures = 0
                    self.state = "CLOSED"
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = current_time
                if self.failures >= self.failure_threshold:
                    logger.error(f"Circuit for {func.__name__} tripped to OPEN after {self.failures} failures. Last error: {e}")
                    self.state = "OPEN"

                if self.fallback:
                    return self.fallback(*args, **kwargs)
                raise
        return wrapper
