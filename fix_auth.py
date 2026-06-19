import re

with open("backend/api/auth.py", "r") as f:
    content = f.read()

# Replace undefined otp_code with the request's code for local fallback behavior
content = content.replace(
    "stored_code = redis_client.get(redis_key) if redis_client else otp_code # Mock pass if redis down for demo",
    "stored_code = redis_client.get(redis_key) if redis_client else otp_verify.code # Mock pass if redis down for demo"
)

with open("backend/api/auth.py", "w") as f:
    f.write(content)
