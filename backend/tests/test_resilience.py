import time

import pytest

from backend.core.resilience import CircuitBreaker, circuit_breaker, with_retries


def test_circuit_breaker_logic():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

    assert breaker.can_execute() == True

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.can_execute() == True

    breaker.record_failure()
    assert breaker.can_execute() == False
    assert breaker.state == "OPEN"

    time.sleep(0.15)
    assert breaker.can_execute() == True
    assert breaker.state == "HALF_OPEN"

    breaker.record_success()
    assert breaker.can_execute() == True
    assert breaker.state == "CLOSED"


def test_with_retries_sync():
    attempts = 0

    @with_retries(max_attempts=3, base_delay=0.01)
    def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        failing_func()

    assert attempts == 3


@pytest.mark.asyncio
async def test_with_retries_async():
    attempts = 0

    @with_retries(max_attempts=3, base_delay=0.01)
    async def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        await failing_func()

    assert attempts == 3


def test_circuit_breaker_decorator():
    attempts = 0

    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        failing_func()
    with pytest.raises(ValueError):
        failing_func()

    # Circuit is now OPEN
    with pytest.raises(Exception, match="Circuit breaker OPEN for failing_func"):
        failing_func()

    assert attempts == 2

    # Test fallback
    @circuit_breaker(
        failure_threshold=1, recovery_timeout=0.1, fallback_func=lambda: "fallback"
    )
    def failing_func2():
        raise ValueError("Failed")

    # first fails and returns fallback? No, it raises or fallback?
    # Let's check our implementation: if fallback_func, does it return on first error?
    # Our implementation:
    #                 except exceptions as e:
    #                    breaker.record_failure()
    #                    if fallback_func:
    #                        return fallback_func(*args, **kwargs)
    #                    raise e

    assert failing_func2() == "fallback"
    # Second time circuit is open, returns fallback without executing
    assert failing_func2() == "fallback"
