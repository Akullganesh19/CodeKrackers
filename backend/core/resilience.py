import asyncio
import functools
import logging
import threading
import time
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception("Circuit is OPEN")

                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e

            return async_wrapper
        else:

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception("Circuit is OPEN")

                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e

            return sync_wrapper

    def _check_state(self):
        with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info("Circuit breaker transitioned to HALF_OPEN")

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                logger.info("Circuit breaker transitioned to CLOSED")

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if (
                self.state in ["CLOSED", "HALF_OPEN"]
                and self.failure_count >= self.failure_threshold
            ):
                self.state = "OPEN"
                logger.warning("Circuit breaker transitioned to OPEN")


def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    time.sleep(delay)

        return wrapper

    return decorator


def with_retry(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)

        return wrapper

    return decorator
