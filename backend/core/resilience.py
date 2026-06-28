import asyncio
import functools
import logging
import time

logger = logging.getLogger("vas.resilience")

def with_retries(max_attempts=3, base_delay=0.1):
    """
    Retry decorator with exponential backoff.
    Raises the last exception if all attempts fail.
    Supports both sync and async functions.
    """
    def decorator(func):
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                            raise
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        await asyncio.sleep(delay)
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if attempt == max_attempts:
                            logger.error(f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}")
                            raise
                        delay = base_delay * (2 ** (attempt - 1))
                        logger.warning(f"Attempt {attempt} failed for {func.__name__}: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
            return sync_wrapper
    return decorator

class CircuitBreakerError(Exception):
    pass

class CircuitBreakerState:
    def __init__(self, failure_threshold, recovery_timeout):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.last_failure_time = None

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit Breaker tripped to OPEN state after {self.failures} failures.")

    def record_success(self):
        if self.state == "HALF-OPEN":
            self.state = "CLOSED"
            logger.info("Circuit Breaker reset to CLOSED state after success in HALF-OPEN.")
        self.failures = 0
        self.last_failure_time = None

    def allow_request(self):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF-OPEN"
                logger.info("Circuit Breaker transitioning to HALF-OPEN state for test request.")
                return True
            return False
        return True

def circuit_breaker(failure_threshold=3, recovery_timeout=60):
    """
    Circuit breaker decorator.
    If failures exceed failure_threshold, the circuit opens and subsequent calls immediately fail
    by raising CircuitBreakerError until recovery_timeout has elapsed.
    """
    def decorator(func):
        state = CircuitBreakerState(failure_threshold, recovery_timeout)

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not state.allow_request():
                    raise CircuitBreakerError(f"Circuit breaker is OPEN for {func.__name__}")

                try:
                    result = await func(*args, **kwargs)
                    state.record_success()
                    return result
                except Exception as e:
                    state.record_failure()
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not state.allow_request():
                    raise CircuitBreakerError(f"Circuit breaker is OPEN for {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    state.record_success()
                    return result
                except Exception as e:
                    state.record_failure()
                    raise
            return sync_wrapper
    return decorator
