import asyncio
import functools
import logging
import time
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

def async_with_retries(max_attempts: int = 3, base_delay: float = 0.1):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise e
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    def decorator(func: Callable):
        state = {"failures": 0, "last_failure_time": 0.0, "state": "CLOSED"}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if state["state"] == "OPEN":
                if now - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} moving to HALF_OPEN")
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Fast failing.")
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if state["state"] == "HALF_OPEN":
                    state["state"] = "CLOSED"
                    state["failures"] = 0
                    logger.info(f"Circuit breaker for {func.__name__} reset to CLOSED")
                return result
            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["state"] = "OPEN"
                    logger.error(f"Circuit breaker for {func.__name__} tripped to OPEN state")
                raise e
        return wrapper
    return decorator

def async_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    def decorator(func: Callable):
        state = {"failures": 0, "last_failure_time": 0.0, "state": "CLOSED"}

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            if state["state"] == "OPEN":
                if now - state["last_failure_time"] > recovery_timeout:
                    state["state"] = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} moving to HALF_OPEN")
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Fast failing.")
                    raise Exception(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
                if state["state"] == "HALF_OPEN":
                    state["state"] = "CLOSED"
                    state["failures"] = 0
                    logger.info(f"Circuit breaker for {func.__name__} reset to CLOSED")
                return result
            except Exception as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["state"] = "OPEN"
                    logger.error(f"Circuit breaker for {func.__name__} tripped to OPEN state")
                raise e
        return wrapper
    return decorator
