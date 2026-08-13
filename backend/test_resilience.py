import pytest
import time
from unittest.mock import MagicMock
from backend.core.resilience import CircuitBreaker, with_retry_sync

def test_circuit_breaker():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    # Mock function that fails
    mock_func = MagicMock(side_effect=Exception("Test failure"))
    mock_func.__name__ = "mock_func"
    wrapped_func = breaker(mock_func)

    with pytest.raises(Exception):
        wrapped_func()
    with pytest.raises(Exception):
        wrapped_func()

    assert breaker.state == "OPEN"

    with pytest.raises(Exception, match="Circuit breaker is OPEN for mock_func"):
        wrapped_func()

    time.sleep(0.15)
    assert breaker.is_open() == False

def test_retry_sync():
    mock_func = MagicMock(side_effect=[Exception("Fail 1"), "Success"])

    @with_retry_sync(max_attempts=3, initial_backoff=0.01)
    def my_func():
        return mock_func()

    assert my_func() == "Success"
    assert mock_func.call_count == 2
