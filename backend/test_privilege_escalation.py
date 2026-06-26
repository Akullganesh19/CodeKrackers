import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.orm import User, UserRole, Base
from backend.api.auth import register_user, UserRegister, verify_otp, OTPVerify, send_otp, OTPSend
from starlette.requests import Request
import unittest.mock
import sys
sys.modules['redis'] = unittest.mock.MagicMock()

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def make_request():
    scope = {
        "type": "http",
        "method": "POST",
        "headers": [(b"host", b"localhost")],
        "path": "/register"
    }
    return Request(scope)

@pytest.mark.asyncio
async def test_register_privilege_escalation():
    # Attempt to register as super_admin
    req = UserRegister(email="hacker@test.com", password="StrongPassword123!", role="super_admin")
    await register_user(db=db, request=make_request(), user_in=req)

    # Assert that the user was NOT created as a super_admin, but as a citizen
    user = db.query(User).filter_by(email="hacker@test.com").first()
    assert user is not None
    assert user.role == UserRole.CITIZEN

@pytest.mark.asyncio
async def test_verify_otp_privilege_escalation():
    # Setup mock OTP code
    from backend.api import auth
    auth.otp_code = "123456"

    # Attempt to verify OTP and escalate privilege
    req_verify = OTPVerify(identifier="hacker_otp@test.com", code="123456", role="super_admin")
    await verify_otp(db=db, otp_verify=req_verify)

    # Assert that the user was NOT created as a super_admin, but as a citizen
    user = db.query(User).filter_by(email="hacker_otp@test.com").first()
    assert user is not None
    assert user.role == UserRole.CITIZEN
