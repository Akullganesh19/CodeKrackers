import asyncio
import functools
import logging
import time
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger("vas.resilience")

RT = TypeVar("RT")

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable[..., RT]) -> Callable[..., RT]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception(f"CircuitBreaker OPEN for {func.__name__}")
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return cast(Callable[..., RT], async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception(f"CircuitBreaker OPEN for {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return cast(Callable[..., RT], sync_wrapper)

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("CircuitBreaker transitioned to HALF_OPEN")

    def _on_success(self):
        self.failure_count = 0
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("CircuitBreaker transitioned to CLOSED")

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state in ("CLOSED", "HALF_OPEN") and self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"CircuitBreaker transitioned to OPEN after {self.failure_count} failures")

def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0, exceptions: tuple = (Exception,)):
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} after error: {e}")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
        return cast(Callable[..., RT], wrapper)
    return decorator

def with_retry_sync(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0, exceptions: tuple = (Exception,)):
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise e
                    logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__} after error: {e}")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
        return cast(Callable[..., RT], wrapper)
    return decorator
