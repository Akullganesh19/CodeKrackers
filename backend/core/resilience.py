import time
import logging
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger("vas.resilience")

def with_retry(max_attempts: int = 3, base_delay: float = 0.5, exceptions: tuple = (Exception,)):
    """
    Decorator for auto-retry with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts. Final error: {e}")
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
