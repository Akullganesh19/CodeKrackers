import asyncio
import time
import logging
from typing import Callable, Any
from functools import wraps

logger = logging.getLogger("vas.resilience")

def with_retry_async(max_attempts: int = 3, base_delay: float = 0.5, backoff_factor: float = 2.0):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Action '{func.__name__}' attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.5, backoff_factor: float = 2.0):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Action '{func.__name__}' attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
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
            def sync_wrapper(*args, **kwargs):
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
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN. Fast failing.")

    def _on_success(self):
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker CLOSED after successful recovery")
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
            if self.state != "OPEN":
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
            self.state = "OPEN"
