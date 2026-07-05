import pytest
import time
from backend.core.resilience import with_retries, circuit_breaker, CircuitBreakerOpenException

def test_with_retries_success():
    attempts = 0
    @with_retries(max_attempts=3, initial_delay=0.01)
    def flaky_func():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Transient error")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert attempts == 3

def test_with_retries_failure():
    @with_retries(max_attempts=2, initial_delay=0.01)
    def failing_func():
        raise ValueError("Persistent error")

    with pytest.raises(ValueError):
        failing_func()

def test_circuit_breaker():
    attempts = 0
    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Error")

    with pytest.raises(ValueError):
        failing_func()

    with pytest.raises(ValueError):
        failing_func()

    with pytest.raises(CircuitBreakerOpenException):
        failing_func()

    time.sleep(0.15)

    with pytest.raises(ValueError):
        failing_func()

if __name__ == "__main__":
    pytest.main(["-v", "test_resilience.py"])
