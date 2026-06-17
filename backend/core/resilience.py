import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, TypeVar, Tuple, Type

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")

def with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Synchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = base_delay
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"[Retry] {func.__name__} failed permanently after {max_attempts} attempts. Last error: {e}")
                        raise
                    logger.warning(f"[Retry] {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {delay}s... Error: {e}")
                    time.sleep(delay)
                    delay = min(delay * 2, max_delay)
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator

def async_with_retries(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Asynchronous retry decorator with exponential backoff.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        logger.error(f"[Retry] Async {func.__name__} failed permanently after {max_attempts} attempts. Last error: {e}")
                        raise
                    logger.warning(f"[Retry] Async {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {delay}s... Error: {e}")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Should not reach here")
        return wrapper
    return decorator

class CircuitBreakerOpenException(Exception):
    """Raised when the circuit breaker is open and requests are blocked."""
    pass

def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Circuit Breaker decorator to prevent cascading failures.
    Trips after `failure_threshold` consecutive failures and stays OPEN for `recovery_timeout`.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        failures = 0
        last_failure_time = 0.0
        state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            nonlocal failures, last_failure_time, state
            now = time.time()
            if state == "OPEN":
                if now - last_failure_time > recovery_timeout:
                    state = "HALF_OPEN"
                    logger.info(f"[CircuitBreaker] {func.__name__} entering HALF_OPEN state.")
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
            except exceptions as e:
                failures += 1
                last_failure_time = time.time()
                if failures >= failure_threshold:
                    state = "OPEN"
                    logger.error(f"[CircuitBreaker] {func.__name__} TRIPPED (OPEN) after {failures} failures.")
                else:
                    logger.warning(f"[CircuitBreaker] {func.__name__} recorded failure ({failures}/{failure_threshold}).")
                raise

            if state == "HALF_OPEN":
                logger.info(f"[CircuitBreaker] {func.__name__} recovered and is now CLOSED.")
            failures = 0
            state = "CLOSED"
            return result
        return wrapper
    return decorator

def async_circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Async Circuit Breaker decorator.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        failures = 0
        last_failure_time = 0.0
        state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal failures, last_failure_time, state
            now = time.time()
            if state == "OPEN":
                if now - last_failure_time > recovery_timeout:
                    state = "HALF_OPEN"
                    logger.info(f"[CircuitBreaker] Async {func.__name__} entering HALF_OPEN state.")
                else:
                    raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {func.__name__}")

            try:
                result = await func(*args, **kwargs)
            except exceptions as e:
                failures += 1
                last_failure_time = time.time()
                if failures >= failure_threshold:
                    state = "OPEN"
                    logger.error(f"[CircuitBreaker] Async {func.__name__} TRIPPED (OPEN) after {failures} failures.")
                else:
                    logger.warning(f"[CircuitBreaker] Async {func.__name__} recorded failure ({failures}/{failure_threshold}).")
                raise

            if state == "HALF_OPEN":
                logger.info(f"[CircuitBreaker] Async {func.__name__} recovered and is now CLOSED.")
            failures = 0
            state = "CLOSED"
            return result
        return wrapper
    return decorator
