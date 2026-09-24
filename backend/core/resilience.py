import functools
import logging
import time

logger = logging.getLogger("vas.resilience")


class CircuitBreakerOpenException(Exception):
    pass


def with_retry_sync(
    max_attempts: int = 3,
    initial_backoff: float = 0.1,
    backoff_factor: float = 2.0,
    exceptions_to_retry: tuple = (Exception,),
):
    """
    Decorator for adding retry logic with exponential backoff to synchronous functions.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            backoff = initial_backoff
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions_to_retry as e:
                    if attempt >= max_attempts:
                        logger.error(
                            f"Function {func.__name__} failed after {max_attempts} attempts. Last error: {e}"
                        )
                        raise

                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt}/{max_attempts}). Retrying in {backoff}s. Error: {e}"
                    )
                    time.sleep(backoff)
                    attempt += 1
                    backoff *= backoff_factor

        return wrapper

    return decorator


class CircuitBreaker:
    """
    Decorator for wrapping external calls in a Circuit Breaker.
    """

    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"  # CLOSED (normal), OPEN (failing), HALF_OPEN (testing)

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # Check if circuit is open
            if self.state == "OPEN":
                if now - self.last_failure_time >= self.recovery_timeout:
                    self.state = "HALF_OPEN"
                    logger.info(
                        f"Circuit breaker for {func.__name__} transitioning to HALF_OPEN state."
                    )
                else:
                    logger.warning(
                        f"Circuit breaker for {func.__name__} is OPEN. Rejecting request."
                    )
                    raise CircuitBreakerOpenException(
                        f"Circuit for {func.__name__} is OPEN"
                    )

            try:
                result = func(*args, **kwargs)

                # If successful in HALF_OPEN, close the circuit
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0
                    logger.info(
                        f"Circuit breaker for {func.__name__} closed after successful test."
                    )

                return result

            except Exception as e:
                # Bypass CircuitBreaker exceptions themselves
                if isinstance(e, CircuitBreakerOpenException):
                    raise

                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.state == "HALF_OPEN":
                    # Failed during test, immediately reopen
                    self.state = "OPEN"
                    logger.warning(
                        f"Circuit breaker for {func.__name__} reopened after test failure."
                    )
                elif (
                    self.failure_count >= self.failure_threshold
                    and self.state == "CLOSED"
                ):
                    # Failed enough times to open circuit
                    self.state = "OPEN"
                    logger.error(
                        f"Circuit breaker for {func.__name__} OPENED after {self.failure_count} failures."
                    )

                raise

        return wrapper
