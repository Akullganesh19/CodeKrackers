import time
import asyncio
import logging
import functools
import threading
from typing import Callable, Any, TypeVar

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

class CircuitBreakerError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_timeout: int = 60, name: str = "default"):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED" # CLOSED, OPEN, HALF_OPEN
        self.name = name
        self._lock = threading.Lock()

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        now = time.time()

        with self._lock:
            if self.state == "OPEN":
                if now - self.last_failure_time >= self.reset_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"CircuitBreaker '{self.name}' state changed to HALF_OPEN. Attempting call.")
                else:
                    raise CircuitBreakerError(f"CircuitBreaker '{self.name}' is OPEN. Call rejected.")

        try:
            result = func(*args, **kwargs)
            with self._lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info(f"CircuitBreaker '{self.name}' state changed to CLOSED. Recovered successfully.")
            return result
        except Exception as e:
            with self._lock:
                self.failures += 1
                self.last_failure_time = now
                if self.failures >= self.max_failures:
                    if self.state != "OPEN":
                        self.state = "OPEN"
                        logger.warning(f"CircuitBreaker '{self.name}' state changed to OPEN. Too many failures ({self.failures}).")
            raise e

    async def call_async(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        now = time.time()

        with self._lock:
            if self.state == "OPEN":
                if now - self.last_failure_time >= self.reset_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"CircuitBreaker '{self.name}' state changed to HALF_OPEN. Attempting call.")
                else:
                    raise CircuitBreakerError(f"CircuitBreaker '{self.name}' is OPEN. Call rejected.")

        try:
            result = await func(*args, **kwargs)
            with self._lock:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info(f"CircuitBreaker '{self.name}' state changed to CLOSED. Recovered successfully.")
            return result
        except Exception as e:
            with self._lock:
                self.failures += 1
                self.last_failure_time = now
                if self.failures >= self.max_failures:
                    if self.state != "OPEN":
                        self.state = "OPEN"
                        logger.warning(f"CircuitBreaker '{self.name}' state changed to OPEN. Too many failures ({self.failures}).")
            raise e

def with_retry_sync(max_attempts: int = 3, initial_backoff_ms: int = 100):
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    backoff = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {backoff} seconds...")
                    time.sleep(backoff)
            raise RuntimeError("Should not be reached")
        return wrapper
    return decorator

def with_retry_async(max_attempts: int = 3, initial_backoff_ms: int = 100):
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    backoff = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
            raise RuntimeError("Should not be reached")
        return wrapper
    return decorator
