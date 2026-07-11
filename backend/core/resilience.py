import asyncio
import functools
import logging
import time
from typing import Callable, TypeVar, Any

logger = logging.getLogger("vas.resilience")

RT = TypeVar("RT")

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is open and requests are being short-circuited."""
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures.")

    def record_success(self):
        if self.state == "HALF-OPEN" or self.state == "OPEN":
            logger.info("Circuit breaker closed. Service recovered.")
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit breaker half-open. Testing service recovery...")
                return True
            return False
        if self.state == "HALF-OPEN":
            # Allow one request to pass through
            return True
        return True

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: int = 30):
    breaker = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> RT:
                if not breaker.can_execute():
                    raise CircuitBreakerOpenException("Circuit breaker is open. Short-circuiting request.")

                try:
                    result = await func(*args, **kwargs)
                    breaker.record_success()
                    return result
                except Exception as e:
                    breaker.record_failure()
                    raise e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> RT:
                if not breaker.can_execute():
                    raise CircuitBreakerOpenException("Circuit breaker is open. Short-circuiting request.")

                try:
                    result = func(*args, **kwargs)
                    breaker.record_success()
                    return result
                except Exception as e:
                    breaker.record_failure()
                    raise e
            return sync_wrapper

    return decorator

def with_retries(max_attempts: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0, max_delay: float = 10.0):
    def decorator(func: Callable[..., RT]) -> Callable[..., RT]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> RT:
                delay = initial_delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if isinstance(e, CircuitBreakerOpenException):
                            raise e

                        if attempt == max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                            raise e

                        logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> RT:
                delay = initial_delay
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if isinstance(e, CircuitBreakerOpenException):
                            raise e

                        if attempt == max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                            raise e

                        logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)
            return sync_wrapper

    return decorator
