import asyncio
import time
import logging
import threading
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Async retry failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def with_retry_sync(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    exceptions: tuple = (Exception,)
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Sync retry failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

class CircuitBreaker:
    STATE_CLOSED = "CLOSED"
    STATE_OPEN = "OPEN"
    STATE_HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0, exceptions: tuple = (Exception,)):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.exceptions = exceptions
        self.state = self.STATE_CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._before_call()
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except self.exceptions:
                    self._on_failure()
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._before_call()
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except self.exceptions:
                    self._on_failure()
                    raise
            return sync_wrapper

    def _before_call(self):
        with self._lock:
            if self.state == self.STATE_OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info("CircuitBreaker transitioning from OPEN to HALF_OPEN")
                    self.state = self.STATE_HALF_OPEN
                else:
                    raise Exception("Circuit is OPEN")

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            if self.state == self.STATE_HALF_OPEN:
                logger.info("CircuitBreaker transitioning from HALF_OPEN to CLOSED")
                self.state = self.STATE_CLOSED

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state in (self.STATE_CLOSED, self.STATE_HALF_OPEN) and self.failure_count >= self.failure_threshold:
                logger.warning(f"CircuitBreaker transitioning to OPEN after {self.failure_count} failures")
                self.state = self.STATE_OPEN
