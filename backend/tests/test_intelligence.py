import pytest
from unittest.mock import MagicMock, patch
from backend.services.intelligence import on_threat_status_changed
from backend.models.orm import Threat, User
from backend.models.threat import ThreatStatus

def test_intelligence_update_scams_avoided():
    # Setup mock db and models
    mock_db = MagicMock()
    mock_threat = MagicMock()
    mock_threat.id = "threat-1"
    mock_threat.user_id = "user-1"

    mock_user = MagicMock()
    mock_user.id = "user-1"
    mock_user.scams_avoided = 5

    # Setup query side effects
    def query_side_effect(model):
        mock_query = MagicMock()
        if model == User:
            mock_query.filter.return_value.first.return_value = mock_user
        elif model == Threat:
            mock_query.filter.return_value.first.return_value = mock_threat
        return mock_query

    mock_db.query.side_effect = query_side_effect

    with patch("backend.services.intelligence.log_event") as mock_log_event:
        on_threat_status_changed(
            threat_id="threat-1",
            new_status=ThreatStatus.resolved.value,
            user_id="user-1",
            client_ip="127.0.0.1",
            db=mock_db
        )

        # Verify log event was called
        mock_log_event.assert_called_once()

        # Verify scams avoided was incremented
        assert mock_user.scams_avoided == 6
        mock_db.commit.assert_called()

def test_intelligence_non_resolved_status():
    mock_db = MagicMock()

    with patch("backend.services.intelligence.log_event") as mock_log_event:
        on_threat_status_changed(
            threat_id="threat-1",
            new_status=ThreatStatus.detected.value,
            user_id="user-1",
            client_ip="127.0.0.1",
            db=mock_db
        )

        # Verify log event was called
        mock_log_event.assert_called_once()

        # Verify db wasn't queried for update
        mock_db.query.assert_not_called()
