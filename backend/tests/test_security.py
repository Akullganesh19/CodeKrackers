import pytest
from backend.core.security import verify_password, get_password_hash, create_access_token, decode_token

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword123!", hashed)

def test_jwt_token():
    subject = "user123"
    role = "admin"
    token = create_access_token(subject=subject, role=role)
    payload = decode_token(token)
    assert payload["sub"] == subject
    assert payload["role"] == role
