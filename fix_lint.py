def replace_in_file(filepath, old, new):
    with open(filepath, 'r') as f:
        content = f.read()
    content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

replace_in_file('backend/api/auth.py', 'stored_code = redis_client.get(redis_key) if redis_client else otp_code', 'stored_code = redis_client.get(redis_key) if redis_client else None')
replace_in_file('backend/services/evidence_chain.py', '{c.name: getattr(b, c.name) for b in b.__table__.columns}', '{c.name: getattr(b, c.name) for c in b.__table__.columns}')
