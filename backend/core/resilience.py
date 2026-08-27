import time
import asyncio
import logging
import threading
from functools import wraps

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()

    def __call__(self, func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise CircuitBreakerOpenException("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise
                self._on_failure()
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with self.lock:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                    else:
                        raise CircuitBreakerOpenException("Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise
                self._on_failure()
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                logger.info("Circuit breaker CLOSED")
                self.state = "CLOSED"

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state in ["CLOSED", "HALF_OPEN"] and self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
                self.state = "OPEN"

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    if attempt == max_retries:
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    time.sleep(delay)
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    if attempt == max_retries:
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
