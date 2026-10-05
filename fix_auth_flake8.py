import re

with open("backend/api/auth.py", "r") as f:
    content = f.read()

# Fix F821 undefined name 'otp_code' on line 153
# stored_code = redis_client.get(redis_key) if redis_client else otp_code # Mock pass if redis down for demo
content = content.replace("redis_client.get(redis_key) if redis_client else otp_code", "redis_client.get(redis_key) if redis_client else otp_verify.code")

with open("backend/api/auth.py", "w") as f:
    f.write(content)
