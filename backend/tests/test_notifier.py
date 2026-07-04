from unittest.mock import patch
from backend.services.notifier import send_threat_alert
import logging
import pytest

def test_send_threat_alert(caplog):
    caplog.set_level(logging.ERROR)
    with patch("backend.services.notifier.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_client.messages.create.side_effect = Exception("Twilio Error")

        with patch("backend.services.notifier.settings") as mock_settings:
            mock_settings.TWILIO_ACCOUNT_SID = "test"
            mock_settings.TWILIO_AUTH_TOKEN = "test"
            mock_settings.TWILIO_PHONE_NUMBER = "test"

            with pytest.raises(Exception):
                send_threat_alert("123", "scam", 0.9, "badguy")

            assert "Failed to send notification" in caplog.text
