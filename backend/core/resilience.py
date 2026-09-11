import time
import logging
from functools import wraps
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger("vas.resilience")

F = TypeVar('F', bound=Callable[..., Any])

class CircuitBreakerOpenException(Exception):
    pass

def CircuitBreaker(failure_threshold: int = 3, recovery_timeout: int = 30) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        func._failure_count = 0
        func._last_failure_time = 0.0
        func._state = "CLOSED" # CLOSED, OPEN, HALF_OPEN

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.time()
            if func._state == "OPEN":
                if now - func._last_failure_time > recovery_timeout:
                    func._state = "HALF_OPEN"
                    logger.info(f"Circuit breaker for {func.__name__} moved to HALF_OPEN")
                else:
                    logger.warning(f"Circuit breaker for {func.__name__} is OPEN. Call rejected.")
                    raise CircuitBreakerOpenException(f"Circuit breaker OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                if func._state == "HALF_OPEN":
                    func._state = "CLOSED"
                    func._failure_count = 0
                    logger.info(f"Circuit breaker for {func.__name__} moved to CLOSED")
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise e
                func._failure_count += 1
                func._last_failure_time = time.time()
                logger.error(f"Execution failed for {func.__name__}: {e}. Failure count: {func._failure_count}")
                if func._failure_count >= failure_threshold:
                    func._state = "OPEN"
                    logger.error(f"Circuit breaker for {func.__name__} moved to OPEN")
                raise e

        return cast(F, wrapper)
    return decorator

def with_retry_sync(max_attempts: int = 3, initial_backoff: float = 0.1, max_backoff: float = 2.0) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            backoff = initial_backoff
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, CircuitBreakerOpenException):
                        raise e
                    if attempt == max_attempts:
                        logger.error(f"All {max_attempts} retry attempts failed for {func.__name__}")
                        raise e
                    logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
        return cast(F, wrapper)
    return decorator
