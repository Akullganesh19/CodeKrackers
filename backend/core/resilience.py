import asyncio
import functools
import logging
import time
from typing import Callable, Any, TypeVar, cast

logger = logging.getLogger("vas.resilience")

T = TypeVar("T", bound=Callable[..., Any])

def with_retries(max_retries: int = 3, base_delay: float = 1.0, exceptions: tuple = (Exception,)) -> Callable[[T], T]:
    """
    Decorator for auto-retry with exponential backoff.
    Works with both sync and async functions.
    """
    def decorator(func: T) -> T:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, max_retries + 1):
                    try:
                        return await func(*args, **kwargs)
                    except CircuitBreakerError:
                        raise
                    except exceptions as e:
                        if attempt == max_retries:
                            logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                            raise
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Function {func.__name__} failed: {e}. Retrying in {delay}s (Attempt {attempt}/{max_retries})")
                        await asyncio.sleep(delay)
            return cast(T, async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                for attempt in range(1, max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except CircuitBreakerError:
                        raise
                    except exceptions as e:
                        if attempt == max_retries:
                            logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                            raise
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Function {func.__name__} failed: {e}. Retrying in {delay}s (Attempt {attempt}/{max_retries})")
                        time.sleep(delay)
            return cast(T, sync_wrapper)
    return decorator

class CircuitBreakerError(Exception):
    pass

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: float = 60.0, exceptions: tuple = (Exception,)) -> Callable[[T], T]:
    """
    Circuit breaker decorator to stop calling a failing dependency.
    """
    def decorator(func: T) -> T:
        state = {"failures": 0, "last_failure_time": 0.0, "state": "CLOSED"}

        def check_circuit():
            if state["state"] == "OPEN":
                if time.time() - state["last_failure_time"] > recovery_timeout:
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to HALF-OPEN")
                    state["state"] = "HALF-OPEN"
                else:
                    raise CircuitBreakerError(f"Circuit for {func.__name__} is OPEN")

        def record_failure():
            state["failures"] += 1
            state["last_failure_time"] = time.time()
            if state["failures"] >= failure_threshold:
                if state["state"] != "OPEN":
                    logger.error(f"Circuit breaker for {func.__name__} transitioning to OPEN")
                state["state"] = "OPEN"

        def record_success():
            if state["state"] == "HALF-OPEN":
                logger.info(f"Circuit breaker for {func.__name__} transitioning to CLOSED")
            state["failures"] = 0
            state["state"] = "CLOSED"

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                check_circuit()
                try:
                    result = await func(*args, **kwargs)
                    record_success()
                    return result
                except exceptions as e:
                    record_failure()
                    raise
            return cast(T, async_wrapper)
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                check_circuit()
                try:
                    result = func(*args, **kwargs)
                    record_success()
                    return result
                except exceptions as e:
                    record_failure()
                    raise
            return cast(T, sync_wrapper)
    return decorator
