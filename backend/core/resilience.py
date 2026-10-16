import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Tuple, Type, TypeVar

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")


def with_retry_sync(
    max_attempts: int = 3,
    base_delay_ms: int = 100,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Synchronous auto-retry decorator with exponential backoff.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay_ms = base_delay_ms * (2 ** (attempt - 1))
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} failed. "
                        f"Retrying in {delay_ms}ms. Error: {e}"
                    )
                    time.sleep(delay_ms / 1000.0)
            raise RuntimeError("Exhausted retries without returning")

        return wrapper

    return decorator


def with_retry_async(
    max_attempts: int = 3,
    base_delay_ms: int = 100,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Asynchronous auto-retry decorator with exponential backoff.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise
                    delay_ms = base_delay_ms * (2 ** (attempt - 1))
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} for {func.__name__} failed. "
                        f"Retrying in {delay_ms}ms. Error: {e}"
                    )
                    await asyncio.sleep(delay_ms / 1000.0)
            raise RuntimeError("Exhausted retries without returning")

        return wrapper

    return decorator


class CircuitBreaker:
    """
    A simple state-based Circuit Breaker.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def _check_state(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("CircuitBreaker entering HALF_OPEN state.")

    def record_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            logger.info("CircuitBreaker successfully recovered. State is now CLOSED.")
        self.failure_count = 0

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if (
            self.state in ["CLOSED", "HALF_OPEN"]
            and self.failure_count >= self.failure_threshold
        ):
            self.state = "OPEN"
            logger.error(
                f"CircuitBreaker tripped! State is now OPEN. Too many failures ({self.failure_count})."
            )

    def __call__(self, fallback_value: Any = None, use_fallback: bool = True):
        """
        Decorator to apply the circuit breaker to a synchronous function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                self._check_state()
                if self.state == "OPEN":
                    logger.warning(
                        f"CircuitBreaker is OPEN. Executing fallback for {func.__name__}."
                    )
                    if use_fallback:
                        return fallback_value
                    raise Exception(f"CircuitBreaker is OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    self.record_success()
                    return result
                except Exception as e:
                    self.record_failure()
                    logger.warning(
                        f"CircuitBreaker recorded failure for {func.__name__}: {e}"
                    )
                    raise

            return wrapper

        return decorator

    def async_call(self, fallback_value: Any = None, use_fallback: bool = True):
        """
        Decorator to apply the circuit breaker to an asynchronous function.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                self._check_state()
                if self.state == "OPEN":
                    logger.warning(
                        f"CircuitBreaker is OPEN. Executing fallback for {func.__name__}."
                    )
                    if use_fallback:
                        return fallback_value
                    raise Exception(f"CircuitBreaker is OPEN for {func.__name__}")

                try:
                    result = await func(*args, **kwargs)
                    self.record_success()
                    return result
                except Exception as e:
                    self.record_failure()
                    logger.warning(
                        f"CircuitBreaker recorded failure for {func.__name__}: {e}"
                    )
                    raise

            return wrapper

        return decorator
