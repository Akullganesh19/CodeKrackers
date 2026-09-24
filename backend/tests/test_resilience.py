import pytest
import time
from backend.core.resilience import CircuitBreaker, with_retry_sync, CircuitBreakerOpenException

def test_retry_sync_success_on_second_try():
    attempts = 0

    @with_retry_sync(max_attempts=3, initial_backoff=0.01)
    def flappy_call():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Failed on purpose")
        return "Success"

    result = flappy_call()
    assert result == "Success"
    assert attempts == 2

def test_retry_sync_failure():
    attempts = 0

    @with_retry_sync(max_attempts=2, initial_backoff=0.01)
    def failing_call():
        nonlocal attempts
        attempts += 1
        raise ValueError("Always fails")

    with pytest.raises(ValueError, match="Always fails"):
        failing_call()

    assert attempts == 2

def test_circuit_breaker():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.2)
    attempts = 0

    @breaker
    def failing_call():
        nonlocal attempts
        attempts += 1
        raise ValueError("Always fails")

    # Attempt 1 -> Failure 1
    with pytest.raises(ValueError):
        failing_call()
    assert attempts == 1
    assert breaker.state == "CLOSED"

    # Attempt 2 -> Failure 2, Circuit Opens
    with pytest.raises(ValueError):
        failing_call()
    assert attempts == 2
    assert breaker.state == "OPEN"

    # Attempt 3 -> Immediately fails with CircuitBreakerOpenException without invoking function
    with pytest.raises(CircuitBreakerOpenException):
        failing_call()
    assert attempts == 2 # Still 2

    # Wait for recovery timeout
    time.sleep(0.3)

    # Attempt 4 -> Half-open, function invoked, fails, opens again
    with pytest.raises(ValueError):
        failing_call()
    assert attempts == 3
    assert breaker.state == "OPEN"

def test_circuit_breaker_recovery():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.1)
    should_fail = True

    @breaker
    def call():
        if should_fail:
            raise ValueError("Failing initially")
        return "Recovered"

    # Attempt 1 -> Fail, Circuit Opens
    with pytest.raises(ValueError):
        call()
    assert breaker.state == "OPEN"

    # Wait for recovery timeout
    time.sleep(0.15)

    # Attempt 2 -> Half-open, succeed, Circuit Closes
    should_fail = False
    result = call()
    assert result == "Recovered"
    assert breaker.state == "CLOSED"
