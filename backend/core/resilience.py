import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger('vas.resilience')

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 30, fallback: Callable = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback

        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF-OPEN

    def _should_attempt(self) -> bool:
        if self.state == 'CLOSED':
            return True
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF-OPEN'
                return True
            return False
        if self.state == 'HALF-OPEN':
            return True
        return False

    def __call__(self, func: Callable):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self._should_attempt():
                    if self.fallback:
                        logger.warning(f'Circuit OPEN for {func.__name__}. Executing fallback.')
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f'Circuit OPEN for {func.__name__}')

                try:
                    result = await func(*args, **kwargs)
                    if self.state == 'HALF-OPEN':
                        logger.info(f'Circuit for {func.__name__} recovered. state=CLOSED')
                        self.state = 'CLOSED'
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        logger.error(f'Circuit for {func.__name__} tripped OPEN after {self.failure_count} failures.')
                        self.state = 'OPEN'
                    if self.fallback:
                        logger.warning(f'Call failed for {func.__name__}, but circuit CLOSED/HALF-OPEN. Executing fallback.')
                        return self.fallback(*args, **kwargs)
                    raise e
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not self._should_attempt():
                    if self.fallback:
                        logger.warning(f'Circuit OPEN for {func.__name__}. Executing fallback.')
                        return self.fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f'Circuit OPEN for {func.__name__}')

                try:
                    result = func(*args, **kwargs)
                    if self.state == 'HALF-OPEN':
                        logger.info(f'Circuit for {func.__name__} recovered. state=CLOSED')
                        self.state = 'CLOSED'
                        self.failure_count = 0
                    return result
                except Exception as e:
                    self.failure_count += 1
                    self.last_failure_time = time.time()
                    if self.failure_count >= self.failure_threshold:
                        logger.error(f'Circuit for {func.__name__} tripped OPEN after {self.failure_count} failures.')
                        self.state = 'OPEN'
                    if self.fallback:
                        logger.warning(f'Call failed for {func.__name__}, but circuit CLOSED/HALF-OPEN. Executing fallback.')
                        return self.fallback(*args, **kwargs)
                    raise e
            return sync_wrapper

def with_retry_sync(max_retries: int = 3, base_delay: float = 0.5):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f'Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay}s due to {e}')
                        time.sleep(delay)
            logger.error(f'All {max_retries} retries failed for {func.__name__}')
            raise last_err
        return wrapper
    return decorator

def with_retry_async(max_retries: int = 3, base_delay: float = 0.5):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f'Retry {attempt + 1}/{max_retries} for {func.__name__} in {delay}s due to {e}')
                        await asyncio.sleep(delay)
            logger.error(f'All {max_retries} retries failed for {func.__name__}')
            raise last_err
        return wrapper
    return decorator
