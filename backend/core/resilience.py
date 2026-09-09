import asyncio
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts=3, base_delay=0.1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"[{func.__name__}] Failed after {max_attempts} attempts: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"[{func.__name__}] Attempt {attempt} failed, retrying in {delay}s...")
                    import time
                    time.sleep(delay)
        return wrapper
    return decorator

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(f"[{func.__name__}] Circuit breaker entering HALF_OPEN state")
                else:
                    logger.warning(f"[{func.__name__}] Circuit breaker OPEN, fast-failing request")
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failures = 0
                    logger.info(f"[{func.__name__}] Circuit breaker reset to CLOSED")
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(f"[{func.__name__}] Circuit breaker tripped OPEN after {self.failures} failures")
                raise e
        return wrapper
