import asyncio
import functools
import logging
import time
from typing import Callable, Any, Optional

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30, fallback: Optional[Callable] = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def __call__(self, func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException("Circuit is OPEN")
                try:
                    result = await func(*args, **kwargs)
                    if self.state in ("HALF_OPEN", "CLOSED"):
                        self.state = "CLOSED"
                        self.failures = 0
                    return result
                except Exception as e:
                    if self.state == "HALF_OPEN":
                        self.state = "OPEN"
                        self.last_failure_time = time.time()
                        logger.warning("CircuitBreaker OPENED from HALF_OPEN")
                        if self.fallback:
                            return self.fallback(*args, **kwargs)
                        raise e
                    self._record_failure()
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException("Circuit is OPEN")
                try:
                    result = func(*args, **kwargs)
                    if self.state in ("HALF_OPEN", "CLOSED"):
                        self.state = "CLOSED"
                        self.failures = 0
                    return result
                except Exception as e:
                    if self.state == "HALF_OPEN":
                        self.state = "OPEN"
                        self.last_failure_time = time.time()
                        logger.warning("CircuitBreaker OPENED from HALF_OPEN")
                        if self.fallback:
                            return self.fallback(*args, **kwargs)
                        raise e
                    self._record_failure()
                    if self.fallback:
                        return self.fallback(*args, **kwargs)
                    raise e
            return sync_wrapper

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                self.failures = 0

    def _record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning("CircuitBreaker OPENED")

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

def with_retry_async(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
