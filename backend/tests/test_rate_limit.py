import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_rate_limit():
    url = "/api/v1/login/access-token"
    data = {"username": "user@example.com", "password": "wrongpassword"}

    # Mock or proper unit test with client
    print("Testing Rate Limiting (5 per minute limit)...")
    for i in range(1, 8):
        response = client.post(url, data=data)
        if response.status_code == 429:
            print("✅ Rate limit triggered successfully!")
            break
