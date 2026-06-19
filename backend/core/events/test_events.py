import pytest
import asyncio
from unittest.mock import patch, MagicMock

from backend.core.events.bus import event_bus
from backend.core.events.listeners import update_user_safety_score_on_threat, setup_listeners

@pytest.mark.asyncio
async def test_event_bus_publish():
    # Verify bus mechanics
    mock_callback = MagicMock()

    event_bus.subscribe("test.event", mock_callback)
    event_bus.publish("test.event", foo="bar")

    # Let asyncio process the sync callback
    await asyncio.sleep(0.1)

    mock_callback.assert_called_once_with("test.event", foo="bar")


@pytest.mark.asyncio
@patch('backend.core.events.listeners.update_user_safety_score_sync')
async def test_listener_integration(mock_sync_update):
    # Setup test
    setup_listeners()

    # Fire the event exactly as the threat system does
    event_bus.publish("threat.created", user_id="123", risk_score=0.8)

    # Let event loop process the async listener
    await asyncio.sleep(0.1)

    # Verify the boundary cross works
    mock_sync_update.assert_called_once_with("123", 0.8)
