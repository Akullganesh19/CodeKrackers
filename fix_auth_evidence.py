import re

with open("backend/api/auth.py", "r") as f:
    content = f.read()

# Fix undefined name 'otp_code' on line 117
content = content.replace("stored_code = redis_client.get(redis_key) if redis_client else otp_code # Mock pass if redis down for demo", "stored_code = redis_client.get(redis_key) if redis_client else otp_verify.code # Mock pass if redis down for demo")

with open("backend/api/auth.py", "w") as f:
    f.write(content)

with open("backend/services/evidence_chain.py", "r") as f:
    content = f.read()

# Fix undefined name 'c' on line 172
# {c.name: getattr(b, c.name) for b in b.__table__.columns} -> {c.name: getattr(b, c.name) for c in b.__table__.columns}
content = content.replace("{c.name: getattr(b, c.name) for b in b.__table__.columns}", "{c.name: getattr(b, c.name) for c in b.__table__.columns}")

with open("backend/services/evidence_chain.py", "w") as f:
    f.write(content)
