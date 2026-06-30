import asyncio
import functools
import logging
import time
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger("vas.resilience")

F = TypeVar('F', bound=Callable[..., Any])

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit is open and calls are prevented."""
    pass

def with_retries(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0) -> Callable[[F], F]:
    """
    Retries the wrapped function with exponential backoff.
    Works with both sync and async functions.
    """
    def decorator(func: F) -> F:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                attempt = 1
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt >= max_attempts:
                            logger.error(f"Retries exhausted for {func.__name__} after {attempt} attempts. Last error: {e}")
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        attempt += 1
            return cast(F, async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                attempt = 1
                while True:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt >= max_attempts:
                            logger.error(f"Retries exhausted for {func.__name__} after {attempt} attempts. Last error: {e}")
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        attempt += 1
            return cast(F, sync_wrapper)
    return decorator

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0) -> Callable[[F], F]:
    """
    Prevents calling the wrapped function if it has failed consecutively more than
    `failure_threshold` times. Allows a test call after `recovery_timeout`.
    Works with both sync and async functions.
    """
    def decorator(func: F) -> F:
        state = {
            "failures": 0,
            "last_failure_time": 0.0,
            "state": "CLOSED" # CLOSED, OPEN, HALF_OPEN
        }

        def check_circuit() -> None:
            if state["state"] == "OPEN":
                if time.time() - state["last_failure_time"] > recovery_timeout:
                    logger.info(f"Circuit HALF_OPEN for {func.__name__}. Testing recovery...")
                    state["state"] = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit OPEN for {func.__name__}. Failing fast.")

        def record_failure() -> None:
            state["failures"] += 1
            state["last_failure_time"] = time.time()
            if state["failures"] >= failure_threshold and state["state"] != "OPEN":
                logger.error(f"Circuit OPENED for {func.__name__} after {state['failures']} failures.")
                state["state"] = "OPEN"

        def record_success() -> None:
            if state["state"] == "HALF_OPEN":
                logger.info(f"Circuit CLOSED for {func.__name__}. Service recovered.")
            state["failures"] = 0
            state["state"] = "CLOSED"

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                check_circuit()
                try:
                    result = await func(*args, **kwargs)
                    record_success()
                    return result
                except Exception as e:
                    if not isinstance(e, CircuitBreakerOpenException):
                        record_failure()
                    raise
            return cast(F, async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                check_circuit()
                try:
                    result = func(*args, **kwargs)
                    record_success()
                    return result
                except Exception as e:
                    if not isinstance(e, CircuitBreakerOpenException):
                        record_failure()
                    raise
            return cast(F, sync_wrapper)
    return decorator
