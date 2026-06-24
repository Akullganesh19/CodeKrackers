import asyncio
import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts: int = 3, base_delay: float = 0.1):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


def async_with_retries(max_attempts: int = 3, base_delay: float = 0.1):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Async function {func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
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
            logger.warning(f"Circuit Breaker opened! Threshold of {self.failure_threshold} failures reached.")

    def record_success(self):
        self.failure_count = 0
        if self.state != "CLOSED":
            logger.info("Circuit Breaker closed. Service recovered.")
        self.state = "CLOSED"

    def is_allowed(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit Breaker half-open. Testing service recovery...")
                return True
            return False
        if self.state == "HALF_OPEN":
            return False # Only allow one request in half-open state, logic should ideally be more robust
        return True


def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_factory: Callable = None):
    """
    Synchronous circuit breaker decorator.
    """
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not cb.is_allowed():
                if fallback_factory:
                    logger.warning(f"Circuit open for {func.__name__}. Executing fallback.")
                    return fallback_factory(*args, **kwargs)
                raise Exception(f"Circuit Breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                if fallback_factory:
                    logger.warning(f"Execution failed for {func.__name__}, but circuit not yet fully open. Executing fallback. Error: {e}")
                    return fallback_factory(*args, **kwargs)
                raise
        return wrapper
    return decorator


def async_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_factory: Callable = None):
    """
    Asynchronous circuit breaker decorator.
    """
    cb = CircuitBreaker(failure_threshold, recovery_timeout)

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not cb.is_allowed():
                if fallback_factory:
                    logger.warning(f"Circuit open for async {func.__name__}. Executing fallback.")
                    return await fallback_factory(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_factory) else fallback_factory(*args, **kwargs)
                raise Exception(f"Circuit Breaker is OPEN for async {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                if fallback_factory:
                    logger.warning(f"Execution failed for async {func.__name__}, but circuit not yet fully open. Executing fallback. Error: {e}")
                    return await fallback_factory(*args, **kwargs) if asyncio.iscoroutinefunction(fallback_factory) else fallback_factory(*args, **kwargs)
                raise
        return wrapper
    return decorator
