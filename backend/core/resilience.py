import logging
import asyncio
import time
from functools import wraps
from typing import Callable, Any, Dict

logger = logging.getLogger("vas.resilience")

def with_retry(max_attempts: int = 3, initial_backoff: float = 0.1):
    """
    Async decorator that retries the wrapped function upon failure.
    Uses exponential backoff: 0.1s, 0.2s, 0.4s...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Action failed after {max_attempts} attempts: {e}")
                        raise

                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed, retrying in {backoff}s...")
                    await asyncio.sleep(backoff)
        return wrapper
    return decorator

def with_retry_sync(max_attempts: int = 3, initial_backoff: float = 0.1):
    """
    Sync decorator that retries the wrapped function upon failure.
    Uses exponential backoff: 0.1s, 0.2s, 0.4s...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Action failed after {max_attempts} attempts: {e}")
                        raise

                    backoff = initial_backoff * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt} failed, retrying in {backoff}s...")
                    time.sleep(backoff)
        return wrapper
    return decorator

def CircuitBreaker(failure_threshold: int = 3, cooldown_seconds: float = 30.0):
    """
    Decorator implementing the Circuit Breaker pattern.
    Stops executing the function and immediately raises an exception
    after `failure_threshold` consecutive failures.
    Restores after `cooldown_seconds`.
    Note: Place this as the OUTERMOST decorator when combining with retries.
    """
    state = "CLOSED"  # CLOSED (normal), OPEN (failing), HALF_OPEN (testing)
    failure_count = 0
    last_failure_time = 0.0

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal state, failure_count, last_failure_time

            now = time.time()

            # Check if we should allow a test request (HALF_OPEN)
            if state == "OPEN":
                if now - last_failure_time >= cooldown_seconds:
                    logger.info(f"CircuitBreaker for {func.__name__} entering HALF_OPEN state.")
                    state = "HALF_OPEN"
                else:
                    raise Exception(f"Circuit for {func.__name__} is OPEN. Fast failing request.")

            try:
                # If we have an async function, we can't cleanly wrap it in the exact same sync
                # wrapper without async handling, but since our target functions are sync,
                # this implementation handles the sync ones.
                # Note: `ai_deep_scan`, `send_threat_alert`, `send_otp`, `openclaw_analysis`, `ollama_deep_scan` are all sync.
                result = func(*args, **kwargs)

                # On success, always reset
                if state in ["HALF_OPEN", "CLOSED"]:
                    if failure_count > 0:
                        logger.info(f"CircuitBreaker for {func.__name__} CLOSED. Resetting failure count.")
                    failure_count = 0
                    state = "CLOSED"
                return result

            except Exception as e:
                # We count a failure
                failure_count += 1
                last_failure_time = time.time()

                if state == "HALF_OPEN":
                    logger.error(f"CircuitBreaker for {func.__name__} failed in HALF_OPEN. Re-opening.")
                    state = "OPEN"
                elif state == "CLOSED" and failure_count >= failure_threshold:
                    logger.error(f"CircuitBreaker for {func.__name__} tripped OPEN after {failure_count} failures.")
                    state = "OPEN"

                raise
        return wrapper
    return decorator
