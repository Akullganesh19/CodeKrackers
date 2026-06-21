import pytest
import requests
import time

def test_rate_limiting_with_server():
    url = "http://localhost:8000/api/v1/login/access-token"
    data = {"username": "user@example.com", "password": "wrongpassword"}

    print("Testing Rate Limiting (5 per minute limit)...")
    try:
        # Try just one to see if server is running
        requests.post(url, data=data)
    except requests.exceptions.ConnectionError:
        pytest.skip("Skipping rate limit test: Server is not running on localhost:8000")

    # Server is up, run real test
    for i in range(1, 8):
        response = requests.post(url, data=data)
        print(f"Attempt {i}: Status {response.status_code}")
        if response.status_code == 429:
            print("✅ Rate limit triggered successfully!")
            assert True
            return
        time.sleep(0.5)

    # If we get here, rate limiting failed
    assert False, "Rate limit of 5/min was not triggered after 7 attempts"
