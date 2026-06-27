import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, TypeVar, Awaitable

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

def with_retries(max_attempts: int = 3, base_delay: float = 0.1, max_delay: float = 2.0, exceptions: tuple = (Exception,)):
    """
    Retry decorator with exponential backoff for both sync and async functions.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    attempt += 1

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed. Retrying in {delay}s...")
                    time.sleep(delay)
                    attempt += 1

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def circuit_breaker(max_failures: int = 5, reset_timeout: float = 60.0):
    """
    Circuit breaker decorator for both sync and async functions.
    """
    class CircuitState:
        def __init__(self):
            self.failures = 0
            self.last_failure_time = 0.0
            self.state = "CLOSED" # CLOSED, OPEN, HALF-OPEN

    state = CircuitState()

    def decorator(func: Callable) -> Callable:
        def _check_circuit():
            now = time.time()
            if state.state == "OPEN":
                if now - state.last_failure_time >= reset_timeout:
                    state.state = "HALF-OPEN"
                    logger.info(f"Circuit for {func.__name__} is HALF-OPEN. Testing next request...")
                else:
                    raise Exception(f"Circuit for {func.__name__} is OPEN. Failing fast.")

        def _handle_success():
            if state.state == "HALF-OPEN":
                state.state = "CLOSED"
                state.failures = 0
                logger.info(f"Circuit for {func.__name__} has recovered and is now CLOSED.")
            elif state.state == "CLOSED":
                state.failures = 0

        def _handle_failure():
            state.failures += 1
            state.last_failure_time = time.time()
            if state.state == "HALF-OPEN":
                state.state = "OPEN"
                logger.error(f"Circuit for {func.__name__} failed in HALF-OPEN state. Reverting to OPEN.")
            elif state.state == "CLOSED" and state.failures >= max_failures:
                state.state = "OPEN"
                logger.error(f"Circuit for {func.__name__} has exceeded {max_failures} failures. State is now OPEN.")

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            _check_circuit()
            try:
                result = await func(*args, **kwargs)
                _handle_success()
                return result
            except Exception as e:
                _handle_failure()
                raise

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            _check_circuit()
            try:
                result = func(*args, **kwargs)
                _handle_success()
                return result
            except Exception as e:
                _handle_failure()
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
