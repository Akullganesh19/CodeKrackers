import asyncio
import time
import logging
from functools import wraps

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0, exceptions=(Exception,)):
    """
    Synchronous decorator for auto-retry with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Action '{func.__name__}' failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Action '{func.__name__}' failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s. Error: {e}")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator

def async_with_retries(max_attempts: int = 3, initial_delay: float = 0.1, backoff_factor: float = 2.0, exceptions=(Exception,)):
    """
    Asynchronous decorator for auto-retry with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Async action '{func.__name__}' failed after {max_attempts} attempts. Last error: {e}")
                        raise e
                    logger.warning(f"Async action '{func.__name__}' failed (attempt {attempt}/{max_attempts}). Retrying in {delay}s. Error: {e}")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
