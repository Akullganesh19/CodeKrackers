import pytest
from unittest.mock import patch, MagicMock

from backend.api import auth
from fastapi import HTTPException
from pydantic import BaseModel
import datetime

class MockOTPVerify(BaseModel):
    identifier: str
    code: str
    role: str = "citizen"

@pytest.mark.asyncio
async def test_otp_verification_without_redis_crashes():
    with patch("backend.api.auth.redis_client", None):
        otp_verify = MockOTPVerify(identifier="test@vsdp.org", code="123456", role="citizen")

        try:
            mock_db = MagicMock()

            # The exact query called is: user = db.query(User).filter( (User.email == ...) | (User.phone_number == ...) ).first()
            # We must make sure the query mock returns a user where locked_until is safely comparable or None
            mock_user = MagicMock()
            mock_user.locked_until = None
            mock_db.query.return_value.filter.return_value.first.return_value = mock_user

            class MockUserCls:
                email = "dummy"
                phone_number = "dummy"

            with patch("backend.api.auth.User", MockUserCls):
                await auth.verify_otp(db=mock_db, otp_verify=otp_verify)
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 503

@pytest.mark.asyncio
async def test_otp_verification_arbitrary_role_assignment():
    with patch("backend.api.auth.redis_client") as mock_redis, \
         patch("backend.api.auth.security.check_account_locked") as mock_locked, \
         patch("backend.api.auth.User") as mock_user_class:

        mock_redis.get.return_value = "123456"
        mock_locked.return_value = False

        mock_user = MagicMock()
        mock_user.id = "fake_id"
        from backend.models.orm import UserRole
        mock_user.role = UserRole("citizen")
        mock_user_class.return_value = mock_user

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        otp_verify = MockOTPVerify(identifier="hacker123@vsdp.org", code="123456", role="admin")

        result = await auth.verify_otp(db=mock_db, otp_verify=otp_verify)

        assert "access_token" in result

        mock_user_class.assert_called_with(
            email="hacker123@vsdp.org",
            phone_number=None,
            is_active=True,
            role=UserRole("citizen")
        )

        from backend.core.security import decode_token
        payload = decode_token(result["access_token"])
        assert payload.get("role") == "citizen"
