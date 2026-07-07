import pytest
import time
import asyncio
from backend.core.resilience import CircuitBreaker, CircuitOpenException, with_retries, circuit_breaker

def test_with_retries_success():
    calls = 0
    @with_retries(max_attempts=3, initial_backoff_ms=10)
    def flacky_func():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("Failed")
        return "Success"

    assert flacky_func() == "Success"
    assert calls == 3

def test_with_retries_failure():
    calls = 0
    @with_retries(max_attempts=3, initial_backoff_ms=10)
    def always_fails():
        nonlocal calls
        calls += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        always_fails()
    assert calls == 3

def test_circuit_breaker():
    calls = 0

    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def always_fails():
        nonlocal calls
        calls += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        always_fails()
    with pytest.raises(ValueError):
        always_fails()

    with pytest.raises(CircuitOpenException):
        always_fails()

    assert calls == 2  # Only called twice, third one blocked by circuit breaker

    # Wait for recovery timeout
    time.sleep(0.15)

    # Try again, it should let one through (half-open)
    with pytest.raises(ValueError):
        always_fails()

    # Should open again immediately
    with pytest.raises(CircuitOpenException):
        always_fails()

    assert calls == 3

@pytest.mark.asyncio
async def test_async_with_retries():
    calls = 0
    @with_retries(max_attempts=2, initial_backoff_ms=10)
    async def async_flacky():
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ValueError("Failed")
        return "Async Success"

    result = await async_flacky()
    assert result == "Async Success"
    assert calls == 2
