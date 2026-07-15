import asyncio
import functools
import logging
import time
from typing import Callable, Type, Tuple

logger = logging.getLogger("vas.resilience")

class CircuitBreakerError(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise CircuitBreakerError(f"Circuit breaker OPEN for {func.__name__}")
                try:
                    result = await func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                if self.state == "OPEN":
                    raise CircuitBreakerError(f"Circuit breaker OPEN for {func.__name__}")
                try:
                    result = func(*args, **kwargs)
                    self._on_success()
                    return result
                except Exception as e:
                    self._on_failure()
                    raise e
            return sync_wrapper

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(f"Circuit breaker transitioned to HALF_OPEN")

    def _on_success(self):
        if self.state == "HALF_OPEN" or self.failures > 0:
            logger.info(f"Circuit breaker transitioned to CLOSED")
            self.failures = 0
            self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.state == "HALF_OPEN" or self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker transitioned to OPEN after {self.failures} failures")

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0):
    return CircuitBreaker(failure_threshold, recovery_timeout)

def with_retries(max_attempts: int = 3, base_delay: float = 0.1, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    def decorator(func: Callable):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except CircuitBreakerError:
                        raise
                    except exceptions as e:
                        if attempt == max_attempts:
                            raise e
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay}s due to: {e}")
                        await asyncio.sleep(delay)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except CircuitBreakerError:
                        raise
                    except exceptions as e:
                        if attempt == max_attempts:
                            raise e
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after {delay}s due to: {e}")
                        time.sleep(delay)
            return sync_wrapper
    return decorator
