import requests
import time

url = "http://localhost:8000/api/v1/login/access-token"
data = {"username": "admin@example.com", "password": "password123"}

print("Testing Rate Limiting (5 per minute limit)...")

for i in range(7):
    response = requests.post(url, data=data)
    print(f"Request {i+1}: Status Code: {response.status_code}")
    if response.status_code == 429:
        print("Rate limit triggered successfully!")
        break
    time.sleep(0.5)
