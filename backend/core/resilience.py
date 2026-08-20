import asyncio
import functools
import logging
import threading
import time
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts: int = 3, backoff_factor: float = 0.5) -> Callable:
    """Synchronous retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {func.__name__} - {str(e)}")
                        raise e
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}, retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, backoff_factor: float = 0.5) -> Callable:
    """Asynchronous retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {func.__name__} - {str(e)}")
                        raise e
                    sleep_time = backoff_factor * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}, retrying in {sleep_time}s...")
                    await asyncio.sleep(sleep_time)
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker decorator pattern to protect against cascading failures.
    Maintains thread-safe state (CLOSED, OPEN, HALF_OPEN).
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to HALF_OPEN")
                    else:
                        raise Exception(f"CircuitBreaker OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                with self._lock:
                    if self.state != "CLOSED" or self.failure_count > 0:
                        self.state = "CLOSED"
                        self.failure_count = 0
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to CLOSED")
                return result
            except Exception as e:
                with self._lock:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"CircuitBreaker for {func.__name__} transitioning to OPEN due to {str(e)}")
                raise e

        return wrapper
