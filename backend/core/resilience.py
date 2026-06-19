import time
import asyncio
import logging
from functools import wraps

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpen(Exception):
    pass

def with_retries(max_retries=3, base_delay=0.1, max_delay=5.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Retry attempt {attempt}/{max_retries} for {func.__name__} failed: {e}")
                    if attempt == max_retries:
                        break
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def async_with_retries(max_retries=3, base_delay=0.1, max_delay=5.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Async retry attempt {attempt}/{max_retries} for {func.__name__} failed: {e}")
                    if attempt == max_retries:
                        break
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

def circuit_breaker(failure_threshold=5, recovery_timeout=30.0, exceptions=(Exception,)):
    def decorator(func):
        state = {"failures": 0, "last_failure_time": 0, "is_open": False}
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if state["is_open"]:
                if current_time - state["last_failure_time"] > recovery_timeout:
                    # Half-open: try once
                    pass
                else:
                    raise CircuitBreakerOpen(f"Circuit for {func.__name__} is OPEN. Try again later.")

            try:
                result = func(*args, **kwargs)
                # Success - close circuit
                state["failures"] = 0
                state["is_open"] = False
                return result
            except exceptions as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["is_open"] = True
                    logger.error(f"Circuit broken for {func.__name__} after {state['failures']} failures.")
                raise e
        return wrapper
    return decorator

def async_circuit_breaker(failure_threshold=5, recovery_timeout=30.0, exceptions=(Exception,)):
    def decorator(func):
        state = {"failures": 0, "last_failure_time": 0, "is_open": False}
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            if state["is_open"]:
                if current_time - state["last_failure_time"] > recovery_timeout:
                    # Half-open: try once
                    pass
                else:
                    raise CircuitBreakerOpen(f"Circuit for {func.__name__} is OPEN. Try again later.")

            try:
                result = await func(*args, **kwargs)
                # Success - close circuit
                state["failures"] = 0
                state["is_open"] = False
                return result
            except exceptions as e:
                state["failures"] += 1
                state["last_failure_time"] = time.time()
                if state["failures"] >= failure_threshold:
                    state["is_open"] = True
                    logger.error(f"Circuit broken for {func.__name__} after {state['failures']} failures.")
                raise e
        return wrapper
    return decorator
