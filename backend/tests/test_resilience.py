import pytest
import asyncio
import time
from backend.core.resilience import with_retries, circuit_breaker, CircuitBreakerError

# --- Retry Tests ---

def test_sync_retries_success():
    attempts = 0

    @with_retries(max_retries=3, base_delay=0.1)
    def flacky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "Success"

    result = flacky_function()
    assert result == "Success"
    assert attempts == 3

def test_sync_retries_failure():
    attempts = 0

    @with_retries(max_retries=3, base_delay=0.1)
    def failing_function():
        nonlocal attempts
        attempts += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError, match="Always fails"):
        failing_function()
    assert attempts == 3

@pytest.mark.asyncio
async def test_async_retries_success():
    attempts = 0

    @with_retries(max_retries=3, base_delay=0.1)
    async def flacky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "Success"

    result = await flacky_function()
    assert result == "Success"
    assert attempts == 3

# --- Circuit Breaker Tests ---

def test_circuit_breaker_opens_and_closes():
    calls = 0

    @circuit_breaker(failure_threshold=2, recovery_timeout=0.2)
    def failing_function(fail: bool):
        nonlocal calls
        calls += 1
        if fail:
            raise ValueError("Failure")
        return "Success"

    # Attempt 1: fail
    with pytest.raises(ValueError):
        failing_function(True)

    # Attempt 2: fail, threshold reached -> OPEN
    with pytest.raises(ValueError):
        failing_function(True)

    assert calls == 2

    # Attempt 3: Circuit is OPEN, should raise CircuitBreakerError immediately without incrementing calls
    with pytest.raises(CircuitBreakerError, match="is OPEN"):
        failing_function(True)

    assert calls == 2

    # Wait for recovery timeout -> HALF-OPEN
    time.sleep(0.3)

    # Attempt 4: Success, circuit closes
    result = failing_function(False)
    assert result == "Success"
    assert calls == 3

    # Attempt 5: Still closed, success
    result = failing_function(False)
    assert result == "Success"
    assert calls == 4

def test_circuit_breaker_bypasses_retry():
    calls = 0

    @with_retries(max_retries=3, base_delay=0.1, exceptions=(Exception,))
    @circuit_breaker(failure_threshold=1, recovery_timeout=60.0)
    def FailingService():
        nonlocal calls
        calls += 1
        raise ValueError("Network Error")

    # Attempt 1: Should fail all 3 retries because Circuit Breaker threshold isn't checked until the inner function runs
    # Wait, the inner function runs, raises ValueError, CB records failure, threshold=1, CB opens.
    # Retry 2 starts, calls CB, CB raises CircuitBreakerError.
    # Our with_retries should NOT catch CircuitBreakerError and immediately raise it.

    with pytest.raises(CircuitBreakerError):
        FailingService()

    # We expect exactly 1 call to the underlying service before the circuit opens.
    assert calls == 1
