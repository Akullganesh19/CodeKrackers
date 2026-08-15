import asyncio
import functools
import logging
import threading
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

def with_retry_sync(max_attempts: int = 3, backoff_factor: float = 2.0, base_delay: float = 0.1):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay = base_delay * (backoff_factor ** (attempt - 1))
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, backoff_factor: float = 2.0, base_delay: float = 0.1):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay = base_delay * (backoff_factor ** (attempt - 1))
                    logger.warning(f"Async function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_timeout: float = 60.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            with self._lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.reset_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"Circuit breaker for {func.__name__} transitioned to HALF_OPEN")
                    else:
                        raise CircuitBreakerOpenException(f"Circuit breaker for {func.__name__} is OPEN")

            try:
                result = func(*args, **kwargs)
                with self._lock:
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"Circuit breaker for {func.__name__} transitioned to CLOSED")
                return result
            except Exception as e:
                with self._lock:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.max_failures:
                        self.state = "OPEN"
                        logger.error(f"Circuit breaker for {func.__name__} transitioned to OPEN after {self.failures} failures. Error: {e}")
                raise e
        return wrapper
