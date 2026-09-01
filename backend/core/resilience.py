import time
import functools
import threading
from typing import Callable, Any, Optional

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Stateful Circuit Breaker pattern.
    If `failure_threshold` sequential failures occur, the circuit opens for `recovery_timeout` seconds.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = 0.0
        self._lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF-OPEN"
                    else:
                        raise CircuitBreakerOpenException(f"Circuit Breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e
        return wrapper

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            self.state = "CLOSED"

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                self.last_failure_time = time.time()

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1, backoff_factor: float = 2.0, exception_types: tuple = (Exception,)):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

# Placeholder for async version if needed in the future
def with_retry(max_retries: int = 3, base_delay: float = 0.1, backoff_factor: float = 2.0, exception_types: tuple = (Exception,)):
    import asyncio
    def decorator(func: Callable) -> Callable:

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exception_types as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
