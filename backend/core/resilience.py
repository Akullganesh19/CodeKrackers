import time
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retry_sync(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, exceptions=(Exception,)):
    """
    Decorator for synchronous functions to retry on failure with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            delay = base_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                        raise
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    attempt += 1
                    delay = min(delay * 2, max_delay)
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

def CircuitBreaker(failure_threshold: int = 3, recovery_timeout: float = 60.0):
    """
    Decorator for synchronous functions to implement a circuit breaker pattern.
    """
    def decorator(func: Callable) -> Callable:
        # State bound to the function
        state = {
            "failures": 0,
            "state": "CLOSED",  # CLOSED, OPEN, HALF_OPEN
            "next_attempt": 0.0
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()

            if state["state"] == "OPEN":
                if now >= state["next_attempt"]:
                    # Transition to HALF_OPEN
                    state["state"] = "HALF_OPEN"
                    logger.info(f"Circuit for {func.__name__} is now HALF_OPEN. Attempting test request.")
                else:
                    logger.warning(f"Circuit for {func.__name__} is OPEN. Rejecting request.")
                    raise CircuitBreakerOpenException(f"Circuit breaker for {func.__name__} is OPEN.")

            try:
                result = func(*args, **kwargs)

                # If we get here, the call succeeded
                if state["state"] != "CLOSED":
                    logger.info(f"Circuit for {func.__name__} recovered. Now CLOSED.")
                    state["state"] = "CLOSED"
                    state["failures"] = 0

                return result

            except Exception as e:
                # Track failure
                state["failures"] += 1
                logger.warning(f"Call to {func.__name__} failed ({state['failures']}/{failure_threshold}): {e}")

                if state["failures"] >= failure_threshold and state["state"] != "OPEN":
                    state["state"] = "OPEN"
                    state["next_attempt"] = now + recovery_timeout
                    logger.error(f"Circuit for {func.__name__} tripped! Now OPEN for {recovery_timeout}s.")

                raise

        return wrapper
    return decorator
