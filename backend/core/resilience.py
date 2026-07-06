import asyncio
import logging
import time
from functools import wraps

logger = logging.getLogger("vas.resilience")


class CircuitBreakerOpenException(Exception):
    pass


async def _retry_logic_async(
    func, args, kwargs, max_attempts, base_delay, max_delay, exceptions
):
    delay = base_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except exceptions as e:
            if attempt == max_attempts:
                logger.error(
                    f"Function {func.__name__} "
                    f"failed after {max_attempts} attempts. "
                    f"Last error: {e}"
                )
                raise
            logger.warning(
                f"Function {func.__name__} "
                f"failed attempt {attempt}/{max_attempts}: "
                f"{e}. Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)


def _retry_logic_sync(
    func, args, kwargs, max_attempts, base_delay, max_delay, exceptions
):
    delay = base_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            if attempt == max_attempts:
                logger.error(
                    f"Function {func.__name__} "
                    f"failed after {max_attempts} attempts. "
                    f"Last error: {e}"
                )
                raise
            logger.warning(
                f"Function {func.__name__} "
                f"failed attempt {attempt}/{max_attempts}: "
                f"{e}. Retrying in {delay}s..."
            )
            time.sleep(delay)
            delay = min(delay * 2, max_delay)


def with_retries(
    max_attempts=3, base_delay=0.1, max_delay=2.0, exceptions=(Exception,)
):
    def decorator(func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _retry_logic_async(
                    func, args, kwargs, max_attempts, base_delay, max_delay, exceptions
                )

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _retry_logic_sync(
                    func, args, kwargs, max_attempts, base_delay, max_delay, exceptions
                )

            return sync_wrapper

    return decorator


class circuit_breaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def __call__(self, func):
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state(func.__name__)
                if self.state == "OPEN":
                    raise CircuitBreakerOpenException(
                        f"Circuit for {func.__name__} is OPEN"
                    )
                try:
                    result = await func(*args, **kwargs)
                    self._on_success(func.__name__)
                    return result
                except Exception as e:
                    self._on_failure(func.__name__)
                    raise e

            return async_wrapper
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state(func.__name__)
                if self.state == "OPEN":
                    raise CircuitBreakerOpenException(
                        f"Circuit for {func.__name__} is OPEN"
                    )
                try:
                    result = func(*args, **kwargs)
                    self._on_success(func.__name__)
                    return result
                except Exception as e:
                    self._on_failure(func.__name__)
                    raise e

            return sync_wrapper

    def _check_state(self, func_name):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info(
                    f"CircuitBreaker for {func_name} entering HALF_OPEN state"
                )

    def _on_success(self, func_name):
        if self.state == "HALF_OPEN" or self.failure_count > 0:
            logger.info(f"CircuitBreaker for {func_name} reset to CLOSED state")
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self, func_name):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == "HALF_OPEN" or self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(
                f"CircuitBreaker for {func_name} entering OPEN state "
                f"after {self.failure_count} failures"
            )
