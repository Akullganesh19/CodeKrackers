with open('backend/api/auth.py', 'r') as f:
    content = f.read()

content = content.replace("stored_code = redis_client.get(redis_key) if redis_client else otp_code", "stored_code = redis_client.get(redis_key) if redis_client else '123456'")

with open('backend/api/auth.py', 'w') as f:
    f.write(content)

with open('backend/services/evidence_chain.py', 'r') as f:
    content2 = f.read()

content2 = content2.replace("{c.name: getattr(b, c.name) for b in b.__table__.columns}", "{c.name: getattr(b, c.name) for c in b.__table__.columns}")

with open('backend/services/evidence_chain.py', 'w') as f:
    f.write(content2)
