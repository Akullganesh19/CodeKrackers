import pytest
import asyncio
from backend.core.events import event_bus
import backend.api.analytics as analytics

@pytest.mark.asyncio
async def test_auth_analytics_connection():
    # Simulate a login event that Auth would emit
    await event_bus.publish('user.login', {
        'user_id': "123-abc",
        'role': "citizen",
        'email': "user@example.com"
    })

    # Let event loop process it
    await asyncio.sleep(0.1)

    assert analytics.login_metrics["total_logins_today"] == 1
    assert analytics.login_metrics["last_login_time"] is not None
