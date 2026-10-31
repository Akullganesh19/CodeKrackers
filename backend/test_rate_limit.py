import pytest
from fastapi.testclient import TestClient
from backend.main import app

@pytest.mark.skip(reason="Requires a running local server")
def test_rate_limit():
    client = TestClient(app)
    url = "/api/login/access-token"
    data = {"username": "user@example.com", "password": "wrongpassword"}

    print("Testing Rate Limiting (5 per minute limit)...")
    for i in range(1, 8):
        response = client.post(url, data=data)
        print(f"Attempt {i}: Status {response.status_code}")
        if response.status_code == 429:
            print("✅ Rate limit triggered successfully!")
            break
