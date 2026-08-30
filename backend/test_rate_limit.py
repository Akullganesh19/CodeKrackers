import requests

url = "http://localhost:8000/api/v1/login/access-token"
data = {
    "username": "admin@example.com",
    "password": "wrongpassword"
}

print("Testing Rate Limiting (5 per minute limit)...")

# Try 6 times in quick succession
for i in range(6):
    response = requests.post(url, data=data)
    print(f"Request {i+1}: Status {response.status_code}")
    if response.status_code == 429:
        print("Success! Rate limit triggered.")
        break
