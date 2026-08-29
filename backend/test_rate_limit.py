import requests
import time
import os

url = "http://localhost:8000/api/v1/login/access-token"
data = {"username": "user@example.com", "password": "wrongpassword"}

print("Testing Rate Limiting (5 per minute limit)...")
# Skip testing HTTP endpoint since server is not running during CI test phase
if os.environ.get("CI") == "true":
    print("Skipping rate limit test in CI environment")
else:
    for i in range(1, 8):
        try:
            response = requests.post(url, data=data)
            print(f"Attempt {i}: Status {response.status_code}")
            if response.status_code == 429:
                print("✅ Rate limit triggered successfully!")
                break
        except requests.exceptions.ConnectionError:
            print("Server not running, skipping test.")
            break
        time.sleep(0.5)
