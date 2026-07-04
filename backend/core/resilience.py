import time
import asyncio
import functools
import logging
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

def with_retries(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0):
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                attempt = 1
                backoff = initial_backoff
                while True:
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt >= max_attempts:
                            raise
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                        attempt += 1
                        backoff *= backoff_factor
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                attempt = 1
                backoff = initial_backoff
                while True:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt >= max_attempts:
                            raise
                        logger.warning(f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. Retrying in {backoff}s...")
                        time.sleep(backoff)
                        attempt += 1
                        backoff *= backoff_factor
            return sync_wrapper
    return decorator

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    def decorator(func: Callable) -> Callable:
        state = {"status": "CLOSED", "failure_count": 0, "last_failure_time": 0.0}

        def _check_state():
            now = time.time()
            if state["status"] == "OPEN":
                if now - state["last_failure_time"] > recovery_timeout:
                    state["status"] = "HALF_OPEN"
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

        def _handle_success():
            if state["status"] == "HALF_OPEN":
                state["status"] = "CLOSED"
                state["failure_count"] = 0

        def _handle_failure():
            state["failure_count"] += 1
            state["last_failure_time"] = time.time()
            if state["failure_count"] >= failure_threshold:
                if state["status"] != "OPEN":
                    logger.error(f"Circuit breaker tripped OPEN for {func.__name__}")
                state["status"] = "OPEN"

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                _check_state()
                try:
                    result = await func(*args, **kwargs)
                    _handle_success()
                    return result
                except Exception as e:
                    _handle_failure()
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                _check_state()
                try:
                    result = func(*args, **kwargs)
                    _handle_success()
                    return result
                except Exception as e:
                    _handle_failure()
                    raise
            return sync_wrapper
    return decorator
