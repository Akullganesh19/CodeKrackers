import pytest
import time
from backend.core.resilience import CircuitBreaker, with_retry_sync

def test_retry():
    calls = 0

    @with_retry_sync(max_retries=3, base_delay=0.01)
    def flippy():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("fail")
        return "success"

    assert flippy() == "success"
    assert calls == 3

def test_circuit_breaker():
    calls = 0
    cb = CircuitBreaker(max_failures=2, reset_timeout=0.1)

    @cb
    def failing():
        nonlocal calls
        calls += 1
        raise ValueError("fail")

    with pytest.raises(ValueError):
        failing()
    assert cb.failures == 1

    with pytest.raises(ValueError):
        failing()
    assert cb.failures == 2
    assert cb.state == "OPEN"

    with pytest.raises(Exception, match="OPEN"):
        failing()
    assert calls == 2

    time.sleep(0.15)
    with pytest.raises(ValueError):
        failing()

    assert cb.state == "OPEN"
    assert calls == 3
