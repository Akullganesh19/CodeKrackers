import time
import asyncio
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Function '{func.__name__}' failed after {max_retries} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for '{func.__name__}' failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

def with_retry_async(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"Async function '{func.__name__}' failed after {max_retries} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for async '{func.__name__}' failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent cascading failures.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0, fallback: Callable = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info("Circuit breaker transitioned to HALF_OPEN")
                    else:
                        if self.fallback:
                            logger.info("Circuit breaker OPEN. Using fallback.")
                            return self.fallback(*args, **kwargs)
                        raise CircuitBreakerOpenException("Circuit breaker is OPEN")

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
            def sync_wrapper(*args, **kwargs):
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info("Circuit breaker transitioned to HALF_OPEN")
                    else:
                        if self.fallback:
                            logger.info("Circuit breaker OPEN. Using fallback.")
                            return self.fallback(*args, **kwargs)
                        raise CircuitBreakerOpenException("Circuit breaker is OPEN")

                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    if not isinstance(e, CircuitBreakerOpenException):
                        self._on_failure()
                    raise
            return sync_wrapper

    def _on_success(self):
        if self.state == "HALF_OPEN" or self.failure_count > 0:
            self.failure_count = 0
            self.state = "CLOSED"
            logger.info("Circuit breaker transitioned to CLOSED")

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state in ["CLOSED", "HALF_OPEN"] and self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error("Circuit breaker transitioned to OPEN")