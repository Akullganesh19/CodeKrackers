import time
import asyncio
import threading
import logging
from functools import wraps
from typing import Callable, Any, TypeVar, Awaitable

logger = logging.getLogger("vas.resilience")

T = TypeVar('T')

class CircuitBreaker:
    """
    A thread-safe Circuit Breaker pattern implementation.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0

        self._lock = threading.Lock()

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        logger.info(f"Circuit Breaker HALF_OPEN for {func.__name__}")
                        self.state = "HALF_OPEN"
                    else:
                        raise Exception(f"Circuit Breaker OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure(func.__name__)
                raise e
        return wrapper

    def _on_success(self):
        with self._lock:
            if self.state in ("HALF_OPEN", "CLOSED"):
                self.failure_count = 0
                if self.state == "HALF_OPEN":
                    logger.info("Circuit Breaker CLOSED")
                self.state = "CLOSED"

    def _on_failure(self, func_name: str):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.warning(f"Circuit Breaker OPEN for {func_name} after {self.failure_count} failures")
                self.state = "OPEN"


def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1, max_delay: float = 5.0):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        break

                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} after error: {e}")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)

            raise last_exception or Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator


def with_retry(max_retries: int = 3, base_delay: float = 0.1, max_delay: float = 5.0):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            delay = base_delay
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        break

                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} after error: {e}")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)

            raise last_exception or Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator
