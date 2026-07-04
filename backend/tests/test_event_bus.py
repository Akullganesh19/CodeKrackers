import pytest
import asyncio
from backend.core.event_bus import event_bus

@pytest.mark.asyncio
async def test_event_bus_sync():
    data = []

    def sync_listener(**kwargs):
        data.append(kwargs.get("test_key"))

    event_bus.subscribe("test_sync", sync_listener)
    event_bus.publish("test_sync", test_key="sync_val")

    assert "sync_val" in data

@pytest.mark.asyncio
async def test_event_bus_async():
    data = []

    async def async_listener(**kwargs):
        data.append(kwargs.get("test_key"))

    event_bus.subscribe("test_async", async_listener)
    event_bus.publish("test_async", test_key="async_val")

    # Wait for the async task to execute
    await asyncio.sleep(0.1)

    assert "async_val" in data
