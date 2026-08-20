from unittest.mock import MagicMock, patch
import pytest

from backend.core.events import EventEmitter

def test_event_bridge_data_flow():
    # Setup the event bus
    bus = EventEmitter()

    # Mock the log_event function to verify cross-boundary flow
    mock_log_event = MagicMock()

    # Simple listener acting as the destination system
    def mock_listener(**kwargs):
        mock_log_event(**kwargs)

    # Wire it up
    bus.on("auth.login_success", mock_listener)

    # Emit data (System A)
    payload = {
        "db": MagicMock(),
        "ip_address": "192.168.1.1",
        "user_id": 42,
        "user_email": "test@example.com",
        "user_agent": "Mozilla/5.0"
    }

    bus.emit("auth.login_success", **payload)

    # Assert data was received (System B)
    mock_log_event.assert_called_once_with(
        db=payload["db"],
        ip_address="192.168.1.1",
        user_id=42,
        user_email="test@example.com",
        user_agent="Mozilla/5.0"
    )

def test_event_listeners_integration():
    from backend.core.events import event_bus
    from backend.services.event_listeners import handle_login_success

    # Verify the listener is properly registered on the global bus
    assert handle_login_success in event_bus._listeners.get("auth.login_success", [])
