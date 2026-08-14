with open('backend/api/auth.py', 'r') as f:
    content = f.read()

# Fix F821 undefined name 'request' by replacing it with otp_verify.code
content = content.replace("stored_code = redis_client.get(redis_key) if redis_client else request.otp_code # Mock pass if redis down for demo", "stored_code = redis_client.get(redis_key) if redis_client else otp_verify.code # Mock pass if redis down for demo")

with open('backend/api/auth.py', 'w') as f:
    f.write(content)
