import pytest
from backend.core.resilience import CircuitBreaker, with_retry_sync, with_retry
import asyncio

def test_circuit_breaker_sync():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    @cb
    def failing_func():
        raise ValueError("Oops")

    with pytest.raises(ValueError):
        failing_func()
    with pytest.raises(ValueError):
        failing_func()

    with pytest.raises(Exception, match="Circuit Breaker OPEN"):
        failing_func()

@pytest.mark.asyncio
async def test_circuit_breaker_async():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

    @cb
    async def failing_func():
        raise ValueError("Oops")

    with pytest.raises(ValueError):
        await failing_func()
    with pytest.raises(ValueError):
        await failing_func()

    with pytest.raises(Exception, match="Circuit Breaker OPEN"):
        await failing_func()

def test_with_retry_sync():
    attempts = 0
    @with_retry_sync(max_attempts=3, base_delay=0.01)
    def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Oops")

    with pytest.raises(ValueError):
        failing_func()

    assert attempts == 3

@pytest.mark.asyncio
async def test_with_retry_async():
    attempts = 0
    @with_retry(max_attempts=3, base_delay=0.01)
    async def failing_func():
        nonlocal attempts
        attempts += 1
        raise ValueError("Oops")

    with pytest.raises(ValueError):
        await failing_func()

    assert attempts == 3
