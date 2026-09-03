import logging
import time
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")

# Simple memory state for Circuit Breaker
# In a real distributed system this would be in Redis
_CB_STATE = {}


def with_retry_sync(max_retries: int = 3, base_delay: float = 0.5):
    """
    Synchronous retry decorator with exponential backoff.
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    # If it's a requests response, raise for status so we can catch and retry
                    if hasattr(result, "raise_for_status"):
                        result.raise_for_status()
                    return result
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} after {delay}s due to: {str(e)}"
                        )
                        time.sleep(delay)
            logger.error(
                f"All {max_retries} retries failed for {func.__name__}: {str(last_exception)}"
            )
            raise last_exception

        return wrapper

    return decorator


class CircuitBreakerOpenException(Exception):
    pass


def CircuitBreaker(
    failure_threshold: int = 3,
    recovery_timeout: float = 30.0,
    fallback: Callable = None,
):
    """
    Circuit breaker decorator to prevent cascading failures.

    States:
    - CLOSED: Normal operation, calls pass through.
    - OPEN: Threshold reached, calls fail fast (or use fallback).
    - HALF_OPEN: Timeout expired, next call tests the service.
    """

    def decorator(func: Callable):
        # We need a unique key for the function in the global state
        key = f"{func.__module__}.{func.__name__}"

        # Initialize state if not present
        if key not in _CB_STATE:
            _CB_STATE[key] = {"state": "CLOSED", "failures": 0, "last_failure_time": 0}

        @wraps(func)
        def wrapper(*args, **kwargs):
            state_info = _CB_STATE[key]

            # Check if OPEN
            if state_info["state"] == "OPEN":
                # Check if recovery timeout has passed
                if time.time() - state_info["last_failure_time"] > recovery_timeout:
                    logger.info(f"Circuit Breaker for {key} entering HALF_OPEN state.")
                    state_info["state"] = "HALF_OPEN"
                else:
                    if fallback:
                        logger.warning(
                            f"Circuit Breaker OPEN for {key}. Using fallback."
                        )
                        return fallback(*args, **kwargs)
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker is OPEN for {key}"
                    )

            # Execute function
            try:
                result = func(*args, **kwargs)

                # If we're here, the call succeeded
                if state_info["state"] == "HALF_OPEN":
                    logger.info(f"Circuit Breaker for {key} closed. Service recovered.")

                # Reset failures on success
                state_info["failures"] = 0
                state_info["state"] = "CLOSED"
                return result

            except Exception as e:
                # Call failed, record it
                state_info["failures"] += 1
                state_info["last_failure_time"] = time.time()

                logger.error(f"Circuit Breaker caught error for {key}: {str(e)}")

                if (
                    state_info["state"] == "HALF_OPEN"
                    or state_info["failures"] >= failure_threshold
                ):
                    if state_info["state"] != "OPEN":
                        logger.critical(
                            f"Circuit Breaker for {key} tripped OPEN! Threshold reached."
                        )
                        state_info["state"] = "OPEN"

                # Re-raise the exception or use fallback
                if fallback:
                    logger.warning(f"Using fallback for {key} after failure.")
                    return fallback(*args, **kwargs)
                raise

        return wrapper

    return decorator
