import asyncio
import logging
from typing import Callable, Any, Type, Union, TypeVar

T = TypeVar('T')

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    """
    Stateful circuit breaker to protect the system from cascading failures.
    Transitions: CLOSED -> OPEN -> HALF_OPEN -> CLOSED/OPEN
    """
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        fallback: Callable[..., Any] = None
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback = fallback

        self.failures = 0
        self.state = "CLOSED"
        self.last_failure_time = 0.0

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        import time
        import inspect

        if inspect.iscoroutinefunction(func):
            async def async_wrapper(*args, **kwargs) -> T:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to HALF_OPEN")
                    else:
                        if self.fallback:
                            logger.warning(f"CircuitBreaker OPEN for {func.__name__}. Using fallback.")
                            return self.fallback(*args, **kwargs)
                        raise CircuitBreakerOpenException(f"Circuit for {func.__name__} is OPEN")

                try:
                    result = await func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to CLOSED")
                    return result
                except Exception as e:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"CircuitBreaker for {func.__name__} transitioning to OPEN due to {e}")
                    if self.fallback:
                        logger.warning(f"Fallback used for {func.__name__} after transient error: {e}")
                        return self.fallback(*args, **kwargs)
                    raise

            return async_wrapper
        else:
            def sync_wrapper(*args, **kwargs) -> T:
                if self.state == "OPEN":
                    if time.time() - self.last_failure_time > self.recovery_timeout:
                        self.state = "HALF_OPEN"
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to HALF_OPEN")
                    else:
                        if self.fallback:
                            logger.warning(f"CircuitBreaker OPEN for {func.__name__}. Using fallback.")
                            return self.fallback(*args, **kwargs)
                        raise CircuitBreakerOpenException(f"Circuit for {func.__name__} is OPEN")

                try:
                    result = func(*args, **kwargs)
                    if self.state == "HALF_OPEN":
                        self.state = "CLOSED"
                        self.failures = 0
                        logger.info(f"CircuitBreaker for {func.__name__} transitioning to CLOSED")
                    return result
                except Exception as e:
                    self.failures += 1
                    self.last_failure_time = time.time()
                    if self.failures >= self.failure_threshold:
                        self.state = "OPEN"
                        logger.error(f"CircuitBreaker for {func.__name__} transitioning to OPEN due to {e}")
                    if self.fallback:
                        logger.warning(f"Fallback used for {func.__name__} after transient error: {e}")
                        return self.fallback(*args, **kwargs)
                    raise

            return sync_wrapper

def with_retry_sync(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exceptions: Union[Type[Exception], tuple] = Exception
):
    """
    Retry decorator with exponential backoff for synchronous functions.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        import time
        def wrapper(*args, **kwargs) -> T:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                        raise

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator

def with_retry_async(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    exceptions: Union[Type[Exception], tuple] = Exception
):
    """
    Retry decorator with exponential backoff for asynchronous functions.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        async def wrapper(*args, **kwargs) -> T:
            attempt = 1
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                        raise

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    attempt += 1
        return wrapper
    return decorator
