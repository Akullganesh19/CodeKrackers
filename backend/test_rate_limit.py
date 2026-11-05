import time
import pytest

@pytest.mark.skip(reason="Requires a running local server")
def test_rate_limit_login():
    url = "http://localhost:8000/api/v1/login/access-token"
    data = {"username": "user@example.com", "password": "wrongpassword"}

    pass
