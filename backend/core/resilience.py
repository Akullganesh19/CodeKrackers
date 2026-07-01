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
    """
    Auto-Retry with Exponential Backoff
    Retries the decorated function on specified exceptions.
    """

    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(
                                f"Final attempt {attempt} failed for {func.__name__}: {e}"
                            )
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts:
                            logger.error(
                                f"Final attempt {attempt} failed for {func.__name__}: {e}"
                            )
                            raise
                        delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s..."
                        )
                        time.sleep(delay)

            return sync_wrapper

    return decorator


def circuit_breaker(failure_threshold=5, recovery_timeout=60.0):
    """
    Circuit Breaker
    Stops calling the service if it fails `failure_threshold` times consecutively.
    Allows testing recovery after `recovery_timeout` seconds.
    """

    def decorator(func):
        failures = 0
        last_failure_time = 0
        state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                nonlocal failures, last_failure_time, state
                current_time = time.time()

                if state == "OPEN":
                    if current_time - last_failure_time > recovery_timeout:
                        state = "HALF_OPEN"
                        logger.info(
                            f"Circuit Breaker for {func.__name__} entering HALF_OPEN state."
                        )
                    else:
                        raise CircuitBreakerOpenException(
                            f"Circuit breaker for {func.__name__} is OPEN."
                        )

                try:
                    result = await func(*args, **kwargs)
                    if state == "HALF_OPEN":
                        state = "CLOSED"
                        failures = 0
                        logger.info(
                            f"Circuit Breaker for {func.__name__} CLOSED. Service recovered."
                        )
                    return result
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    failures += 1
                    last_failure_time = time.time()
                    if (
                        state in ["CLOSED", "HALF_OPEN"]
                        and failures >= failure_threshold
                    ):
                        state = "OPEN"
                        logger.error(
                            f"Circuit Breaker for {func.__name__} TRIPPED OPEN after {failures} failures."
                        )
                    raise

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                nonlocal failures, last_failure_time, state
                current_time = time.time()

                if state == "OPEN":
                    if current_time - last_failure_time > recovery_timeout:
                        state = "HALF_OPEN"
                        logger.info(
                            f"Circuit Breaker for {func.__name__} entering HALF_OPEN state."
                        )
                    else:
                        raise CircuitBreakerOpenException(
                            f"Circuit breaker for {func.__name__} is OPEN."
                        )

                try:
                    result = func(*args, **kwargs)
                    if state == "HALF_OPEN":
                        state = "CLOSED"
                        failures = 0
                        logger.info(
                            f"Circuit Breaker for {func.__name__} CLOSED. Service recovered."
                        )
                    return result
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise
                    failures += 1
                    last_failure_time = time.time()
                    if (
                        state in ["CLOSED", "HALF_OPEN"]
                        and failures >= failure_threshold
                    ):
                        state = "OPEN"
                        logger.error(
                            f"Circuit Breaker for {func.__name__} TRIPPED OPEN after {failures} failures."
                        )
                    raise

            return sync_wrapper

    return decorator
