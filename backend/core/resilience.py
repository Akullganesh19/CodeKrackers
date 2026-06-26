import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

def with_retries(
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for synchronous functions to retry on failure with exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"[{func.__name__}] Failed after {max_attempts} attempts. Last error: {e}")
                        raise
                    logger.warning(f"[{func.__name__}] Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator

def async_with_retries(
    max_attempts: int = 3,
    initial_delay: float = 0.5,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator for asynchronous functions to retry on failure with exponential backoff.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"[{func.__name__}] Failed after {max_attempts} attempts. Last error: {e}")
                        raise
                    logger.warning(f"[{func.__name__}] Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
            raise RuntimeError("Unreachable")
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    pass

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    exceptions: tuple = (Exception,),
    fallback: Callable[..., Any] = None,
) -> Callable:
    """
    Synchronous circuit breaker decorator.
    If `fallback` is provided, it returns fallback(*args, **kwargs) when open or failing.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        state = {
            "failures": 0,
            "last_failure_time": 0.0,
            "state": "CLOSED" # CLOSED, OPEN, HALF_OPEN
        }

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()

            if state["state"] == "OPEN":
                if current_time - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF_OPEN"
                    logger.info(f"[{func.__name__}] Circuit breaker transitioning to HALF_OPEN")
                else:
                    if fallback:
                        return fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"[{func.__name__}] Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)

                # Success on HALF_OPEN -> close the circuit
                if state["state"] == "HALF_OPEN":
                    state["state"] = "CLOSED"
                    state["failures"] = 0
                    logger.info(f"[{func.__name__}] Circuit breaker transitioning to CLOSED (recovered)")

                return result
            except exceptions as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()

                if state["state"] == "HALF_OPEN" or state["failures"] >= failure_threshold:
                    state["state"] = "OPEN"
                    logger.warning(f"[{func.__name__}] Circuit breaker transitioning to OPEN after {state['failures']} failures. Last error: {e}")

                if fallback:
                    return fallback(*args, **kwargs)
                raise
        return wrapper
    return decorator

def async_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    exceptions: tuple = (Exception,),
    fallback: Callable[..., Any] = None,
) -> Callable:
    """
    Asynchronous circuit breaker decorator.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        state = {
            "failures": 0,
            "last_failure_time": 0.0,
            "state": "CLOSED"
        }

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_time = time.time()

            if state["state"] == "OPEN":
                if current_time - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF_OPEN"
                    logger.info(f"[{func.__name__}] Circuit breaker transitioning to HALF_OPEN")
                else:
                    if fallback:
                        if asyncio.iscoroutinefunction(fallback):
                            return await fallback(*args, **kwargs)
                        return fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(f"[{func.__name__}] Circuit breaker is OPEN")

            try:
                result = await func(*args, **kwargs)

                if state["state"] == "HALF_OPEN":
                    state["state"] = "CLOSED"
                    state["failures"] = 0
                    logger.info(f"[{func.__name__}] Circuit breaker transitioning to CLOSED (recovered)")

                return result
            except exceptions as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()

                if state["state"] == "HALF_OPEN" or state["failures"] >= failure_threshold:
                    state["state"] = "OPEN"
                    logger.warning(f"[{func.__name__}] Circuit breaker transitioning to OPEN after {state['failures']} failures. Last error: {e}")

                if fallback:
                    if asyncio.iscoroutinefunction(fallback):
                        return await fallback(*args, **kwargs)
                    return fallback(*args, **kwargs)
                raise
        return wrapper
    return decorator
