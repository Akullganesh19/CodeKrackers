import pytest
import asyncio
from backend.core.events.bus import event_bus
from backend.core.events.listeners import on_user_locked, setup_listeners
from backend.core.database import SessionLocal
from backend.models.orm import Threat, ThreatType
import uuid

@pytest.mark.asyncio
async def test_user_locked_event_bridge():
    # Trigger the event
    data = {
        "user_id": str(uuid.uuid4()),
        "email": "hacker@example.com",
        "ip_address": "192.168.1.100"
    }

    # Directly invoke the handler for testing
    on_user_locked(data)

    # Check the database for the newly created threat
    db = SessionLocal()
    threat = db.query(Threat).filter(Threat.sender_id == "192.168.1.100").order_by(Threat.detected_at.desc()).first()

    assert threat is not None
    assert threat.severity.value == "high" or threat.severity == "high"
    assert "hacker@example.com" in threat.raw_content
    assert threat.user_id == data["user_id"]

    # Cleanup
    db.delete(threat)
    db.commit()
    db.close()
