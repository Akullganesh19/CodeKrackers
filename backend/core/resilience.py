import asyncio
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for synchronous functions to add retry logic with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    logger.warning(f"Function {func.__name__} attempt {attempt} failed. Retrying in {delay}s. Error: {e}")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            return None # Should not be reached
        return wrapper
    return decorator

def async_with_retries(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Decorator for asynchronous functions to add retry logic with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    logger.warning(f"Async function {func.__name__} attempt {attempt} failed. Retrying in {delay}s. Error: {e}")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            return None
        return wrapper
    return decorator

class CircuitBreaker:
    """
    A simple Circuit Breaker implementation to protect external dependencies.
    """
    def __init__(self, max_failures: int = 3, reset_timeout: float = 60.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = "CLOSED" # "CLOSED", "OPEN", "HALF_OPEN"
        self.last_failure_time = 0.0

    def _check_state(self):
        import time
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker moved to HALF_OPEN state")

    def call(self, func: Callable, *args, **kwargs):
        self._check_state()
        if self.state == "OPEN":
            logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Call rejected.")
            raise Exception("Circuit Breaker OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(f"Circuit breaker for {func.__name__} moved to CLOSED state")
            return result
        except Exception as e:
            self.failures += 1
            import time
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures:
                self.state = "OPEN"
                logger.error(f"Circuit breaker for {func.__name__} moved to OPEN state after {self.failures} failures. Error: {e}")
            raise

    async def async_call(self, func: Callable, *args, **kwargs):
        self._check_state()
        if self.state == "OPEN":
            logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Call rejected.")
            raise Exception("Circuit Breaker OPEN")

        try:
            result = await func(*args, **kwargs)
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0
                logger.info(f"Circuit breaker for {func.__name__} moved to CLOSED state")
            return result
        except Exception as e:
            self.failures += 1
            import time
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures:
                self.state = "OPEN"
                logger.error(f"Circuit breaker for {func.__name__} moved to OPEN state after {self.failures} failures. Error: {e}")
            raise

def circuit_breaker(max_failures: int = 3, reset_timeout: float = 60.0):
    cb = CircuitBreaker(max_failures, reset_timeout)
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        return wrapper
    return decorator

def async_circuit_breaker(max_failures: int = 3, reset_timeout: float = 60.0):
    cb = CircuitBreaker(max_failures, reset_timeout)
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.async_call(func, *args, **kwargs)
        return wrapper
    return decorator
