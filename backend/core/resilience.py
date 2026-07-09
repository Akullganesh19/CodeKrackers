import logging
import time
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")


def with_retries(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    max_backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            backoff = initial_backoff
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}"  # noqa: E501
                        )
                        raise e
                    logger.warning(
                        f"Function {func.__name__} failed attempt {attempt}/{max_attempts}. Retrying in {backoff}s. Error: {e}"  # noqa: E501
                    )
                    time.sleep(backoff)
                    attempt += 1
                    backoff = min(backoff * 2, max_backoff)

        return wrapper

    return decorator


class CircuitBreakerOpenException(Exception):
    pass


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()
            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(
                        f"Circuit breaker for {func.__name__} entering HALF-OPEN state."
                    )
                    self.state = "HALF-OPEN"
                else:
                    logger.warning(
                        f"Circuit breaker for {func.__name__} is OPEN. Call blocked."
                    )
                    raise CircuitBreakerOpenException(
                        f"Circuit for {func.__name__} is open."
                    )

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(
                        f"Circuit breaker for {func.__name__} entering CLOSED state after successful call."  # noqa: E501
                    )
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                if isinstance(e, CircuitBreakerOpenException):
                    raise
                self.failures += 1
                self.last_failure_time = now
                if self.failures >= self.failure_threshold:
                    logger.error(
                        f"Circuit breaker for {func.__name__} entering OPEN state after {self.failures} failures. Error: {e}"  # noqa: E501
                    )
                    self.state = "OPEN"
                raise

        return wrapper


def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0):
    return CircuitBreaker(failure_threshold, recovery_timeout)
