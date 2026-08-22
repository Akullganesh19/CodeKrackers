import time
import asyncio
import threading
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.5):
    """
    Synchronous exponential backoff retry decorator.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

def with_retry(max_attempts: int = 3, base_delay: float = 0.5):
    """
    Asynchronous exponential backoff retry decorator.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

class CircuitBreaker:
    """
    Circuit breaker decorator to protect against cascading failures.
    State transitions:
    - CLOSED: Normal operation. If failures reach failure_threshold, switch to OPEN.
    - OPEN: Calls immediately fail. After cooldown_seconds, switch to HALF_OPEN.
    - HALF_OPEN: Next call is allowed. If success, switch to CLOSED. If failure, switch to OPEN.
    """
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: float = 60.0):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds

        self.state = "CLOSED"
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.cooldown_seconds:
                        self.state = "HALF_OPEN"
                        logger.info(f"Circuit Breaker for {func.__name__} is now HALF_OPEN")
                    else:
                        raise Exception(f"Circuit breaker for {func.__name__} is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success(func.__name__)
                return result
            except Exception as e:
                self._on_failure(func.__name__)
                raise e
        return wrapper

    def _on_success(self, func_name: str):
        with self.lock:
            if self.state == "HALF_OPEN" or self.failure_count > 0:
                if self.state == "HALF_OPEN":
                    logger.info(f"Circuit Breaker for {func_name} is now CLOSED")
                self.state = "CLOSED"
                self.failure_count = 0

    def _on_failure(self, func_name: str):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
                if self.state != "OPEN":
                    logger.warning(f"Circuit Breaker for {func_name} is now OPEN")
                self.state = "OPEN"
