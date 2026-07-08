import functools
import logging
import time
import asyncio
from typing import Any, Callable, Type, Tuple, Union

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
):
    """
    Retries the wrapped function upon exceptions with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                attempt = 1
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt >= max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Function {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {delay}s. Error: {e}")
                        await asyncio.sleep(delay)
                        attempt += 1
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                attempt = 1
                while True:
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt >= max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(f"Function {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {delay}s. Error: {e}")
                        time.sleep(delay)
                        attempt += 1
            return sync_wrapper
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
):
    """
    Circuit breaker pattern to fail fast when an external service is down.
    """
    def decorator(func: Callable) -> Callable:
        state = {
            "failures": 0,
            "last_failure_time": 0.0,
            "state": "CLOSED" # CLOSED, OPEN, HALF_OPEN
        }

        def _check_circuit():
            if state["state"] == "OPEN":
                if time.time() - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} entering HALF_OPEN state.")
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker for {func.__name__} is OPEN.")

        def _on_success():
            if state["state"] == "HALF_OPEN":
                state["state"] = "CLOSED"
                state["failures"] = 0
                logger.info(f"Circuit breaker for {func.__name__} entering CLOSED state.")
            elif state["state"] == "CLOSED":
                state["failures"] = 0

        def _on_failure():
            state["failures"] += 1
            state["last_failure_time"] = time.time()
            if state["state"] == "HALF_OPEN" or state["failures"] >= failure_threshold:
                if state["state"] != "OPEN":
                    logger.error(f"Circuit breaker for {func.__name__} entering OPEN state after {state['failures']} failures.")
                state["state"] = "OPEN"

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                _check_circuit()
                try:
                    result = await func(*args, **kwargs)
                    _on_success()
                    return result
                except exceptions:
                    _on_failure()
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                _check_circuit()
                try:
                    result = func(*args, **kwargs)
                    _on_success()
                    return result
                except exceptions:
                    _on_failure()
                    raise
            return sync_wrapper
    return decorator
