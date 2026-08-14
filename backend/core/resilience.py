import time
import asyncio
import functools
import threading
from typing import Callable

class CircuitBreaker:
    def __init__(self, max_failures: int = 3, reset_timeout: float = 60.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.lock = threading.Lock()

    def __call__(self, func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.lock:
                    if self.state == "OPEN":
                        if time.time() - self.last_failure_time > self.reset_timeout:
                            self.state = "HALF-OPEN"
                        else:
                            raise Exception(f"CircuitBreaker is OPEN for {func.__name__}")

                try:
                    result = await func(*args, **kwargs)
                    with self.lock:
                        if self.state == "HALF-OPEN":
                            self.state = "CLOSED"
                        self.failures = 0
                    return result
                except Exception as e:
                    with self.lock:
                        self.failures += 1
                        self.last_failure_time = time.time()
                        if self.failures >= self.max_failures:
                            self.state = "OPEN"
                    raise e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.lock:
                    if self.state == "OPEN":
                        if time.time() - self.last_failure_time > self.reset_timeout:
                            self.state = "HALF-OPEN"
                        else:
                            raise Exception(f"CircuitBreaker is OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    with self.lock:
                        if self.state == "HALF-OPEN":
                            self.state = "CLOSED"
                        self.failures = 0
                    return result
                except Exception as e:
                    with self.lock:
                        self.failures += 1
                        self.last_failure_time = time.time()
                        if self.failures >= self.max_failures:
                            self.state = "OPEN"
                    raise e
            return sync_wrapper

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(base_delay * (2 ** attempt))
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(base_delay * (2 ** attempt))
        return wrapper
    return decorator
