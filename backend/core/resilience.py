import asyncio
import logging
import threading
import time
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_period: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                self._check_state()
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    if not isinstance(e, CircuitBreakerOpenException):
                        self._on_failure()
                    raise

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                self._check_state()
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    if not isinstance(e, CircuitBreakerOpenException):
                        self._on_failure()
                    raise

            return sync_wrapper

    def _check_state(self):
        with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.cooldown_period:
                    self.state = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException("Circuit breaker is OPEN")

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"


def with_retry_sync(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            backoff = initial_backoff
            while attempt < max_attempts:
                attempt += 1
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt} for {func.__name__} failed, retrying in {backoff}s..."
                    )
                    time.sleep(backoff)
                    backoff *= backoff_factor

        return wrapper

    return decorator


def with_retry(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            backoff = initial_backoff
            while attempt < max_attempts:
                attempt += 1
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt} for {func.__name__} failed, retrying in {backoff}s..."
                    )
                    await asyncio.sleep(backoff)
                    backoff *= backoff_factor

        return wrapper

    return decorator
