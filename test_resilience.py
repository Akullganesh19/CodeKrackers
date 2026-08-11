import pytest
from backend.core.resilience import with_retry

def test_retry():
    attempts = 0

    @with_retry(max_attempts=3, base_delay=0.01)
    def flaky_func():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ValueError("Failed")
        return "Success"

    assert flaky_func() == "Success"
    assert attempts == 3
