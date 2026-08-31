import time
import logging
import asyncio
from functools import wraps
import threading

logger = logging.getLogger("vas.resilience")

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"
        self._lock = threading.Lock()

    def __call__(self, func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception(f"Circuit Breaker is OPEN for {func.__name__}")
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise Exception(f"Circuit Breaker is OPEN for {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return sync_wrapper

    def _check_state(self):
        with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    logger.info("Circuit Breaker transitioning from OPEN to HALF_OPEN")
                    self.state = "HALF_OPEN"

    def _on_success(self):
        with self._lock:
            self.failure_count = 0
            if self.state == "HALF_OPEN":
                logger.info("Circuit Breaker transitioning from HALF_OPEN to CLOSED")
                self.state = "CLOSED"

    def _on_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.state in ["CLOSED", "HALF_OPEN"] and self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit Breaker transitioning to OPEN (failures: {self.failure_count})")
                self.state = "OPEN"

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__} after {delay}s due to {e}")
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
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry {attempt}/{max_retries} for {func.__name__} after {delay}s due to {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
