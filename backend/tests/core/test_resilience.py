import pytest
import time
from backend.core.resilience import with_retries, circuit_breaker, CircuitBreakerOpenException

def test_with_retries_success_first_try():
    calls = 0

    @with_retries(max_attempts=3, initial_backoff=0.01)
    def my_func():
        nonlocal calls
        calls += 1
        return "success"

    assert my_func() == "success"
    assert calls == 1

def test_with_retries_success_after_failure():
    calls = 0

    @with_retries(max_attempts=3, initial_backoff=0.01)
    def my_func():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("Failed")
        return "success"

    assert my_func() == "success"
    assert calls == 3

def test_with_retries_failure():
    calls = 0

    @with_retries(max_attempts=3, initial_backoff=0.01)
    def my_func():
        nonlocal calls
        calls += 1
        raise ValueError("Failed")

    with pytest.raises(ValueError):
        my_func()
    assert calls == 3

def test_circuit_breaker():
    calls = 0

    @circuit_breaker(failure_threshold=2, recovery_timeout=0.1)
    def my_func(should_fail=False):
        nonlocal calls
        calls += 1
        if should_fail:
            raise ValueError("Failed")
        return "success"

    assert my_func() == "success"

    with pytest.raises(ValueError):
        my_func(should_fail=True)

    with pytest.raises(ValueError):
        my_func(should_fail=True)

    with pytest.raises(CircuitBreakerOpenException):
        my_func()

    time.sleep(0.15)

    assert my_func() == "success"
