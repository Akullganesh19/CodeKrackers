import asyncio
import time
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit Breaker for {func.__name__} entering HALF-OPEN state")
                    self.state = "HALF-OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit Breaker for {func.__name__} is OPEN")
            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(f"Circuit Breaker for {func.__name__} entering CLOSED state")
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    logger.error(f"Circuit Breaker for {func.__name__} entering OPEN state due to {e}")
                    self.state = "OPEN"
                raise

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit Breaker for {func.__name__} entering HALF-OPEN state")
                    self.state = "HALF-OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit Breaker for {func.__name__} is OPEN")
            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(f"Circuit Breaker for {func.__name__} entering CLOSED state")
                    self.state = "CLOSED"
                    self.failure_count = 0
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    logger.error(f"Circuit Breaker for {func.__name__} entering OPEN state due to {e}")
                    self.state = "OPEN"
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0, exceptions: tuple = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    if attempt == max_retries:
                        logger.error(f"Sync Retry for {func.__name__} failed after {max_retries} attempts. Last error: {e}")
                        raise
                    logger.warning(f"Sync Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 0.5, max_delay: float = 5.0, exceptions: tuple = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    if attempt == max_retries:
                        logger.error(f"Async Retry for {func.__name__} failed after {max_retries} attempts. Last error: {e}")
                        raise
                    logger.warning(f"Async Retry {attempt + 1}/{max_retries} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator
