import time
import asyncio
import logging
from functools import wraps
from enum import Enum
import threading

logger = logging.getLogger("vas.resilience")

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class CircuitBreaker:
    def __init__(self, max_failures=3, cooldown=60):
        self.max_failures = max_failures
        self.cooldown = cooldown
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0
        self.lock = threading.Lock()

    def __call__(self, func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == CircuitState.OPEN:
                    logger.warning(f"Circuit breaker OPEN for {func.__name__}")
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
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
                if self.state == CircuitState.OPEN:
                    logger.warning(f"Circuit breaker OPEN for {func.__name__}")
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return sync_wrapper

    def _check_state(self):
        with self.lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.cooldown:
                    logger.info(f"Circuit breaker HALF_OPEN after cooldown")
                    self.state = CircuitState.HALF_OPEN

    def _on_success(self):
        with self.lock:
            self.failure_count = 0
            if self.state == CircuitState.HALF_OPEN:
                logger.info(f"Circuit breaker CLOSED after successful request")
                self.state = CircuitState.CLOSED

    def _on_failure(self):
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.max_failures and self.state != CircuitState.OPEN:
                logger.warning(f"Circuit breaker tripped to OPEN after {self.failure_count} failures")
                self.state = CircuitState.OPEN

def with_retry_sync(max_attempts=3, base_delay=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} in {delay}s due to {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

def with_retry(max_attempts=3, base_delay=0.1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} in {delay}s due to {e}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
