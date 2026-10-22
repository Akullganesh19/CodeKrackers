import functools
import logging
import asyncio
import time
from typing import Callable, Any, Optional

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts: int = 3, initial_backoff_ms: int = 100) -> Callable:
    """
    Decorator for synchronous functions to automatically retry on exception
    using exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                        raise

                    backoff = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {backoff}s. Error: {e}")
                    time.sleep(backoff)
                    attempt += 1
        return wrapper
    return decorator

def with_retry_async(max_attempts: int = 3, initial_backoff_ms: int = 100) -> Callable:
    """
    Decorator for asynchronous functions to automatically retry on exception
    using exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                        raise

                    backoff = (initial_backoff_ms * (2 ** (attempt - 1))) / 1000.0
                    logger.warning(f"Async function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {backoff}s. Error: {e}")
                    await asyncio.sleep(backoff)
                    attempt += 1
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    A simple Circuit Breaker for protecting against cascading failures.
    State machine: CLOSED (normal) -> OPEN (failing, fast fail) -> HALF_OPEN (testing recovery) -> CLOSED/OPEN
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout_sec: float = 30.0, fallback: Optional[Callable] = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.fallback = fallback

        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = 0.0

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()

            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout_sec:
                    logger.info(f"Circuit Breaker for {func.__name__} entering HALF_OPEN state.")
                    self.state = "HALF_OPEN"
                else:
                    if self.fallback:
                        logger.warning(f"Circuit Breaker OPEN for {func.__name__}. Executing fallback.")
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"Circuit Breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)

                if self.state == "HALF_OPEN":
                    logger.info(f"Circuit Breaker for {func.__name__} recovered. Entering CLOSED state.")
                    self.state = "CLOSED"
                    self.failures = 0
                elif self.state == "CLOSED":
                    # Ensure failures reset to 0 on successful execution when closed.
                    self.failures = 0

                return result

            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()

                if self.state == "HALF_OPEN" or self.failures >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.error(f"Circuit Breaker for {func.__name__} tripped! Entering OPEN state. Error: {e}")
                    self.state = "OPEN"

                if self.fallback:
                    logger.warning(f"Execution failed for {func.__name__}, but fallback provided. Executing fallback.")
                    return self.fallback(*args, **kwargs)
                raise

        return wrapper
