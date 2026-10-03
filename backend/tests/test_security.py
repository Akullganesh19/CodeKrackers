import pytest
from backend.core.security import verify_password, get_password_hash

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)

    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False

def test_verify_password_with_malformed_hash():
    assert verify_password("password", "malformed_hash") is False
    assert verify_password("password", None) is False
