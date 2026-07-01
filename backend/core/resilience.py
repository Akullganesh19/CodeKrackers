import asyncio
import logging
import time
from functools import wraps

logger = logging.getLogger("vas.resilience")


class CircuitBreakerOpenException(Exception):
    pass


def with_retries(
    max_attempts=3, base_delay=0.1, max_delay=2.0, exceptions=(Exception,)
):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _retry_logic(
                    True,
                    func,
                    max_attempts,
                    base_delay,
                    max_delay,
                    exceptions,
                    *args,
                    **kwargs,
                )

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _retry_logic(
                    False,
                    func,
                    max_attempts,
                    base_delay,
                    max_delay,
                    exceptions,
                    *args,
                    **kwargs,
                )

            return sync_wrapper

    return decorator


async def _retry_logic(
    is_async, func, max_attempts, base_delay, max_delay, exceptions, *args, **kwargs
):
    for attempt in range(1, max_attempts + 1):
        try:
            if is_async:
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions:
            if attempt == max_attempts:
                logger.error("Final fail %s %s" % (attempt, func.__name__))
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            logger.warning("Fail %s %s" % (attempt, func.__name__))
            if is_async:
                await asyncio.sleep(delay)
            else:
                time.sleep(delay)


def circuit_breaker(failure_threshold=5, recovery_timeout=60.0):
    def decorator(func):
        state = {"failures": 0, "last_failure_time": 0, "status": "CLOSED"}

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                _check_circuit(state, func.__name__, recovery_timeout)
                try:
                    result = await func(*args, **kwargs)
                    _record_success(state, func.__name__)
                    return result
                except Exception as e:
                    _record_failure(state, func.__name__, e, failure_threshold)
                    raise

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                _check_circuit(state, func.__name__, recovery_timeout)
                try:
                    result = func(*args, **kwargs)
                    _record_success(state, func.__name__)
                    return result
                except Exception as e:
                    _record_failure(state, func.__name__, e, failure_threshold)
                    raise

            return sync_wrapper

    return decorator


def _check_circuit(state, func_name, recovery_timeout):
    current_time = time.time()
    if state["status"] == "OPEN":
        if current_time - state["last_failure_time"] > recovery_timeout:
            state["status"] = "HALF_OPEN"
            logger.info("CB for %s HALF_OPEN" % func_name)
        else:
            raise CircuitBreakerOpenException("OPEN")


def _record_success(state, func_name):
    if state["status"] == "HALF_OPEN":
        state["status"] = "CLOSED"
        state["failures"] = 0
        logger.info("CB for %s CLOSED" % func_name)


def _record_failure(state, func_name, exception, failure_threshold):
    if isinstance(exception, CircuitBreakerOpenException):
        return
    state["failures"] += 1
    state["last_failure_time"] = time.time()
    if (
        state["status"] in ["CLOSED", "HALF_OPEN"]
        and state["failures"] >= failure_threshold
    ):
        state["status"] = "OPEN"
        logger.error("CB for %s TRIPPED OPEN" % func_name)
