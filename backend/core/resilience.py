import asyncio
import time
import logging
import threading
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Synchronous decorator to retry a function with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_backoff = initial_backoff
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Sync Retry failed after {max_attempts} attempts for {func.__name__}: {e}")
                        raise e
                    logger.warning(f"Sync Retry {attempt}/{max_attempts} for {func.__name__} after {current_backoff}s backoff due to: {e}")
                    time.sleep(current_backoff)
                    current_backoff *= backoff_factor
                    attempt += 1
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Asynchronous decorator to retry a function with exponential backoff.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 1
            current_backoff = initial_backoff
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Async Retry failed after {max_attempts} attempts for {func.__name__}: {e}")
                        raise e
                    logger.warning(f"Async Retry {attempt}/{max_attempts} for {func.__name__} after {current_backoff}s backoff due to: {e}")
                    await asyncio.sleep(current_backoff)
                    current_backoff *= backoff_factor
                    attempt += 1
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Thread-safe Circuit Breaker pattern to protect against cascading failures
    from external dependencies.
    """
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()

    def call(self, func: Callable, *args, **kwargs) -> Any:
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info("CircuitBreaker transitioning to HALF_OPEN")
                    self.state = "HALF_OPEN"
                else:
                    raise Exception("CircuitBreaker is OPEN. Fast-failing request.")

        try:
            result = func(*args, **kwargs)

            with self.lock:
                if self.state == "HALF_OPEN":
                    logger.info("CircuitBreaker transitioning to CLOSED")
                    self.state = "CLOSED"
                self.failure_count = 0

            return result

        except Exception as e:
            with self.lock:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.warning(f"CircuitBreaker transitioning to OPEN after {self.failure_count} failures.")
                        self.state = "OPEN"

            raise e
