import asyncio
import time
import functools
import logging
from typing import Callable, Any
import threading

logger = logging.getLogger("vas.resilience")

import httpx
import requests

def _is_transient_error(e: Exception) -> bool:
    """Helper to determine if an HTTP error is deterministic/client error (like 4xx) and shouldn't be retried."""
    if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
        if 400 <= e.response.status_code < 500:
            return False
    if isinstance(e, httpx.HTTPStatusError):
        if 400 <= e.response.status_code < 500:
            return False
    return True


def with_retry_sync(max_retries: int = 3, base_delay: float = 0.5):
    """
    Synchronous decorator for retrying a function with exponential backoff.
    Only retries on transient errors, skips deterministic 4xx client errors.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not _is_transient_error(e):
                        logger.warning(f"Function {func.__name__} encountered deterministic error: {e}. Aborting retries.")
                        raise
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Function {func.__name__} attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

def with_retry(max_retries: int = 3, base_delay: float = 0.5):
    """
    Asynchronous decorator for retrying a function with exponential backoff.
    Only retries on transient errors, skips deterministic 4xx client errors.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = base_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if not _is_transient_error(e):
                        logger.warning(f"Async function {func.__name__} encountered deterministic error: {e}. Aborting retries.")
                        raise
                    if attempt == max_retries:
                        logger.error(f"Async function {func.__name__} failed after {max_retries} attempts: {e}")
                        raise
                    logger.warning(f"Async function {func.__name__} attempt {attempt} failed: {e}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

class CircuitBreaker:
    """
    A thread-safe decorator for implementing the Circuit Breaker pattern.
    Transitions states between CLOSED (normal), OPEN (failing, block calls),
    and HALF_OPEN (testing if recovered).
    """
    def __init__(self, max_failures: int = 3, reset_timeout: float = 30.0):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.last_failure_time = 0.0
        self.lock = threading.Lock()
        self.func_name = "unknown"

    def __call__(self, func: Callable):
        self.func_name = func.__name__

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                self._check_state()
                try:
                    result = await func(*args, **kwargs)
                    self._record_success()
                    return result
                except Exception as e:
                    self._record_failure(e)
                    raise
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                self._check_state()
                try:
                    result = func(*args, **kwargs)
                    self._record_success()
                    return result
                except Exception as e:
                    self._record_failure(e)
                    raise
            return sync_wrapper

    def _check_state(self):
        with self.lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time > self.reset_timeout:
                    logger.info(f"Circuit Breaker for {self.func_name} transitioning to HALF_OPEN")
                    self.state = "HALF_OPEN"
                else:
                    raise Exception(f"Circuit Breaker is OPEN for {self.func_name}")

    def _record_success(self):
        with self.lock:
            if self.state == "HALF_OPEN":
                logger.info(f"Circuit Breaker for {self.func_name} transitioning to CLOSED")
                self.state = "CLOSED"
            self.failures = 0

    def _record_failure(self, e: Exception):
        with self.lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.state == "HALF_OPEN" or self.failures >= self.max_failures:
                if self.state != "OPEN":
                    logger.warning(f"Circuit Breaker for {self.func_name} transitioning to OPEN due to: {e}")
                self.state = "OPEN"
