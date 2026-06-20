import asyncio
import functools
import logging
import time
from typing import Any, Callable

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts: int = 3, base_delay: float = 0.1, exceptions: tuple = (Exception,)):
    """
    Decorator that retries a synchronous function on failure with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise e

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt}/{max_attempts} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

def async_with_retries(max_attempts: int = 3, base_delay: float = 0.1, exceptions: tuple = (Exception,)):
    """
    Decorator that retries an asynchronous function on failure with exponential backoff.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(f"Async function {func.__name__} failed after {max_attempts} attempts. Error: {e}")
                        raise e

                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(f"Attempt {attempt}/{max_attempts} for async {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

class CircuitBreaker:
    """
    A simple state machine circuit breaker for synchronous functions.
    States:
      - CLOSED: Normal operation. If consecutive failures > threshold, trip to OPEN.
      - OPEN: Fast fail or return fallback. After recovery_timeout, switch to HALF-OPEN.
      - HALF-OPEN: One attempt allowed. If succeeds, CLOSED. If fails, OPEN.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_func: Callable = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback_func = fallback_func

        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = 0.0

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            now = time.time()

            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit for {func.__name__} half-open. Testing...")
                    self.state = "HALF-OPEN"
                else:
                    if self.fallback_func:
                        logger.warning(f"Circuit for {func.__name__} is OPEN. Using fallback.")
                        return self.fallback_func(*args, **kwargs)
                    raise Exception(f"Circuit for {func.__name__} is OPEN.")

            try:
                result = func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(f"Circuit for {func.__name__} recovered. Closing circuit.")
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()

                if self.state == "HALF-OPEN" or self.failures >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.error(f"Circuit for {func.__name__} TRIPPED OPEN after {self.failures} failures. Error: {e}")
                    self.state = "OPEN"

                if self.fallback_func:
                    return self.fallback_func(*args, **kwargs)
                raise e
        return wrapper

def circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_func: Callable = None):
    return CircuitBreaker(failure_threshold, recovery_timeout, fallback_func)

class AsyncCircuitBreaker:
    """
    A simple state machine circuit breaker for asynchronous functions.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_func: Callable = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback_func = fallback_func

        self.state = "CLOSED"
        self.failures = 0
        self.last_failure_time = 0.0

    def __call__(self, func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            now = time.time()

            if self.state == "OPEN":
                if now - self.last_failure_time > self.recovery_timeout:
                    logger.info(f"Circuit for async {func.__name__} half-open. Testing...")
                    self.state = "HALF-OPEN"
                else:
                    if self.fallback_func:
                        logger.warning(f"Circuit for async {func.__name__} is OPEN. Using fallback.")
                        # Check if fallback is coroutine
                        if asyncio.iscoroutinefunction(self.fallback_func):
                            return await self.fallback_func(*args, **kwargs)
                        else:
                            return self.fallback_func(*args, **kwargs)
                    raise Exception(f"Circuit for async {func.__name__} is OPEN.")

            try:
                result = await func(*args, **kwargs)
                if self.state == "HALF-OPEN":
                    logger.info(f"Circuit for async {func.__name__} recovered. Closing circuit.")
                    self.state = "CLOSED"
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()

                if self.state == "HALF-OPEN" or self.failures >= self.failure_threshold:
                    if self.state != "OPEN":
                        logger.error(f"Circuit for async {func.__name__} TRIPPED OPEN after {self.failures} failures. Error: {e}")
                    self.state = "OPEN"

                if self.fallback_func:
                    if asyncio.iscoroutinefunction(self.fallback_func):
                        return await self.fallback_func(*args, **kwargs)
                    else:
                        return self.fallback_func(*args, **kwargs)
                raise e
        return wrapper

def async_circuit_breaker(failure_threshold: int = 3, recovery_timeout: float = 30.0, fallback_func: Callable = None):
    return AsyncCircuitBreaker(failure_threshold, recovery_timeout, fallback_func)
