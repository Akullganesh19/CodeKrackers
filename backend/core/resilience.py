import functools
import time
import logging
import asyncio
from typing import Callable, Any

logger = logging.getLogger("vas.resilience")

class CircuitBreakerOpenException(Exception):
    pass

def with_retries(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """Retry a synchronous function with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            backoff = initial_backoff
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Max retries ({max_attempts}) reached for {func.__name__}: {e}")
                        raise e
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after {backoff}s due to: {e}")
                    time.sleep(backoff)
                    attempt += 1
                    backoff *= backoff_factor
        return wrapper
    return decorator

def async_with_retries(max_attempts: int = 3, initial_backoff: float = 0.1, backoff_factor: float = 2.0, exceptions: tuple = (Exception,)):
    """Retry an asynchronous function with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            backoff = initial_backoff
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt >= max_attempts:
                        logger.error(f"Max retries ({max_attempts}) reached for {func.__name__}: {e}")
                        raise e
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__} after {backoff}s due to: {e}")
                    await asyncio.sleep(backoff)
                    attempt += 1
                    backoff *= backoff_factor
        return wrapper
    return decorator

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, exceptions: tuple = (Exception,)):
    """Fail fast after threshold failures, allowing recovery after timeout (synchronous)."""
    def decorator(func: Callable) -> Callable:
        failures = 0
        last_failure_time = 0.0

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            nonlocal failures, last_failure_time
            now = time.time()
            if failures >= failure_threshold:
                if now - last_failure_time < recovery_timeout:
                    raise CircuitBreakerOpenException(f"Circuit breaker open for {func.__name__}")
                else:
                    # Half-open state
                    logger.info(f"Circuit breaker half-open for {func.__name__}, attempting recovery.")

            try:
                result = func(*args, **kwargs)
                # Success -> reset circuit
                if failures > 0:
                    logger.info(f"Circuit breaker closed for {func.__name__}")
                failures = 0
                return result
            except exceptions as e:
                failures += 1
                last_failure_time = time.time()
                logger.warning(f"Circuit breaker failure {failures}/{failure_threshold} for {func.__name__}: {e}")
                raise e
        return wrapper
    return decorator

def async_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, exceptions: tuple = (Exception,)):
    """Fail fast after threshold failures, allowing recovery after timeout (asynchronous)."""
    def decorator(func: Callable) -> Callable:
        failures = 0
        last_failure_time = 0.0

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            nonlocal failures, last_failure_time
            now = time.time()
            if failures >= failure_threshold:
                if now - last_failure_time < recovery_timeout:
                    raise CircuitBreakerOpenException(f"Circuit breaker open for {func.__name__}")
                else:
                    logger.info(f"Circuit breaker half-open for {func.__name__}, attempting recovery.")

            try:
                result = await func(*args, **kwargs)
                if failures > 0:
                    logger.info(f"Circuit breaker closed for {func.__name__}")
                failures = 0
                return result
            except exceptions as e:
                failures += 1
                last_failure_time = time.time()
                logger.warning(f"Circuit breaker failure {failures}/{failure_threshold} for {func.__name__}: {e}")
                raise e
        return wrapper
    return decorator
