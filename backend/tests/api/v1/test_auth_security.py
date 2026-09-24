import pytest
import asyncio
from backend.api.auth import UserRegister, OTPVerify, verify_otp
from pydantic import ValidationError

def test_mass_assignment_user_register():
    try:
        ur = UserRegister(email="test@test.com", password="Password123!", role="super_admin")
        assert not hasattr(ur, 'role'), "UserRegister should not accept role field"
    except ValidationError:
        pass # Expected and valid

def test_mass_assignment_otp_verify():
    try:
        ov = OTPVerify(identifier="test@test.com", code="123456", role="super_admin")
        assert not hasattr(ov, 'role'), "OTPVerify should not accept role field"
    except ValidationError:
        pass # Expected and valid

@pytest.mark.asyncio
async def test_nameerror_on_redis_down():
    from backend.models.orm import User
    # Mocking deps
    class MockUser:
         locked_until = None
         role = "citizen"
         failed_login_attempts = 0
         id = "123"
    class MockUserQuery:
        def filter(self, *args): return self
        def first(self): return MockUser()
    class MockDB:
        def query(self, *args): return MockUserQuery()
        def add(self, *args): pass
        def commit(self, *args): pass
        def refresh(self, *args): pass

    try:
        await verify_otp(db=MockDB(), otp_verify=OTPVerify(identifier="test@test.com", code="123"))
    except NameError as e:
        pytest.fail(f"NameError triggered: {e}")
    except Exception as e:
        assert "Invalid or expired verification code" in str(e)
