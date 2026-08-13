import asyncio
import time
import logging
import threading
from typing import TypeVar, Callable, Any
from functools import wraps

logger = logging.getLogger("vas.resilience")

T = TypeVar('T')


def with_retry(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    max_backoff: float = 2.0,
    exceptions_to_catch: tuple = (Exception,)
):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            backoff = initial_backoff
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions_to_catch as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__} - {str(e)}"
                        )
                        raise e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. Retrying in {backoff}s..."
                    )
                    await asyncio.sleep(backoff)
                    attempt += 1
                    backoff = min(backoff * 2, max_backoff)
        return wrapper
    return decorator


def with_retry_sync(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    max_backoff: float = 2.0,
    exceptions_to_catch: tuple = (Exception,)
):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            backoff = initial_backoff
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_catch as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts: {func.__name__} - {str(e)}"
                        )
                        raise e
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}. Retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    attempt += 1
                    backoff = min(backoff * 2, max_backoff)
        return wrapper
    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def _update_state(self):
        with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"

    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.error(f"Circuit Breaker OPENED after {self.failure_count} failures.")

    def record_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"

    def is_open(self):
        self._update_state()
        return self.state == "OPEN"

    def __call__(self, func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.is_open():
                logger.warning(f"Circuit breaker OPEN. Fast-failing {func.__name__}.")
                raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise e
        return wrapper
