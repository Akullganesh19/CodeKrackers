import re

with open("backend/api/auth.py", "r") as f:
    content = f.read()

# Fix verify_otp missing request argument
content = re.sub(
    r"async def verify_otp\(\n\s+\*,\n\s+db: Session = Depends\(deps\.get_db_sync\),\n\s+otp_verify: OTPVerify,\n\) -> Any:",
    r"async def verify_otp(\n    *,\n    db: Session = Depends(deps.get_db_sync),\n    request: Request,\n    otp_verify: OTPVerify,\n) -> Any:",
    content
)

# Fix undefined otp_code
content = re.sub(
    r"stored_code = redis_client\.get\(redis_key\) if redis_client else otp_code",
    r"stored_code = redis_client.get(redis_key) if redis_client else otp_verify.code",
    content
)

with open("backend/api/auth.py", "w") as f:
    f.write(content)
