import asyncio
from backend.core.resilience import with_retries, circuit_breaker, CircuitBreakerOpenException
import time

fail_count = 0

@with_retries(max_attempts=3, base_delay=0.1, max_delay=1.0)
@circuit_breaker(failure_threshold=2, recovery_timeout=0.5)
async def my_failing_function():
    global fail_count
    fail_count += 1
    if fail_count < 5:
        raise ValueError("Simulated failure")
    return "Success"

async def main():
    try:
        await my_failing_function()
    except Exception as e:
        print(f"Failed: {e}")

    print("Waiting for circuit to recover...")
    await asyncio.sleep(0.6)

    try:
        result = await my_failing_function()
        print(f"Result after recovery: {result}")
    except Exception as e:
         print(f"Failed again: {e}")

if __name__ == "__main__":
    asyncio.run(main())
