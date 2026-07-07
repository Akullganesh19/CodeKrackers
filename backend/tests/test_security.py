from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword!", hashed)


def test_jwt():
    token = create_access_token(subject="user@example.com")
    payload = decode_token(token)
    assert payload["sub"] == "user@example.com"
