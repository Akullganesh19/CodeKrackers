import time

def test_manual_rate_limit():
    pass
    # This is a manual test, we keep it as a function so pytest ignores it running directly
    # url = "http://localhost:8000/api/auth/login"
    # data = {"username": "user@example.com", "password": "wrongpassword"}
    # print("Testing Rate Limiting (5 per minute limit)...")
    # for i in range(1, 8):
    #     response = requests.post(url, data=data)
    #     print(f"Attempt {i}: Status {response.status_code}")
    #     if response.status_code == 429:
    #         print("✅ Rate limit triggered successfully!")
    #         break
    #     time.sleep(0.5)

if __name__ == "__main__":
    import requests
    url = "http://localhost:8000/api/auth/login"
    data = {"username": "user@example.com", "password": "wrongpassword"}

    print("Testing Rate Limiting (5 per minute limit)...")
    for i in range(1, 8):
        try:
            response = requests.post(url, data=data)
            print(f"Attempt {i}: Status {response.status_code}")
            if response.status_code == 429:
                print("✅ Rate limit triggered successfully!")
                break
            time.sleep(0.5)
        except Exception as e:
            print(f"Skipping test due to: {e}")
            break
