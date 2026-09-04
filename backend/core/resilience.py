import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, TypeVar

logger = logging.getLogger("vas.resilience")

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Failing, failing fast
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class CircuitBreaker:
    """
    Stateful circuit breaker that prevents cascading failures.
    Should be instantiated globally for a given service.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0.0

    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    logger.info(f"Circuit Breaker testing recovery for {func.__name__}")
                    self.state = CircuitState.HALF_OPEN
                else:
                    logger.warning(
                        f"Circuit Breaker OPEN for {func.__name__} - failing fast"
                    )
                    raise Exception(f"Circuit Breaker OPEN for {func.__name__}")

            try:
                result = func(*args, **kwargs)
                self._on_success(func.__name__)
                return result
            except Exception as e:
                self._on_failure(func.__name__, e)
                raise e

        return wrapper

    def _on_success(self, name: str):
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit Breaker RECOVERED for {name}")
            self.state = CircuitState.CLOSED

    def _on_failure(self, name: str, e: Exception):
        self.failure_count += 1
        self.last_failure_time = time.time()
        logger.error(f"Circuit Breaker recorded failure for {name}: {e}")
        if (
            self.failure_count >= self.failure_threshold
            and self.state != CircuitState.OPEN
        ):
            logger.critical(
                f"Circuit Breaker TRIPPED OPEN for {name} after {self.failure_count} failures"
            )
            self.state = CircuitState.OPEN


def with_retry_sync(max_retries: int = 3, base_delay: float = 0.1) -> Callable:
    """
    Synchronous retry decorator with exponential backoff.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(
                            f"Failed {func.__name__} after {max_retries} attempts: {e}"
                        )
                        raise e

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Retry {attempt}/{max_retries} for {func.__name__} in {delay}s due to: {e}"
                    )
                    time.sleep(delay)
            # This should never be reached due to the raise in the loop above
            raise Exception("Retry logic failed")

        return wrapper

    return decorator
