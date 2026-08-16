import asyncio
import time
import logging
import threading
from functools import wraps
from typing import Callable, Any, TypeVar, cast, Awaitable

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

def with_retry(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)) -> Callable:
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            backoff = initial_backoff
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
                    attempt += 1
                    backoff *= backoff_factor
        return wrapper
    return decorator

def with_retry_sync(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)) -> Callable:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempt = 1
            backoff = initial_backoff
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    attempt += 1
                    backoff *= backoff_factor
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0
        self.lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                self._check_state()
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                self._check_state()
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return sync_wrapper

    def _check_state(self):
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("CircuitBreaker transitioned to HALF_OPEN")
                else:
                    raise CircuitBreakerOpenException("Circuit is OPEN")

    def _on_success(self):
        with self.lock:
            if self.state in ["HALF_OPEN", "OPEN"]:
                logger.info("CircuitBreaker transitioned to CLOSED (Recovery successful)")
            self.failure_count = 0
            self.state = "CLOSED"

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.error(f"CircuitBreaker transitioned to OPEN after {self.failure_count} failures")
                self.state = "OPEN"
