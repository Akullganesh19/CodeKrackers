import requests
import time

url = "http://localhost:8000/api/login/access-token"
data = {"username": "user@example.com", "password": "wrongpassword"}

print("Testing Rate Limiting (5 per minute limit)...")
for i in range(1, 8):
    response = requests.post(url, data=data)
    print(f"Attempt {i}: Status {response.status_code}")
    if response.status_code == 429:
        print("✅ Rate limit triggered successfully!")
        break
    time.sleep(0.5)
