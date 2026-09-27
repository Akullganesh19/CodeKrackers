import re

with open('backend/api/auth.py', 'r') as f:
    auth_content = f.read()

# Fix undefined name 'otp_code'
# otp_code is from line 117. It appears to be an attempt to use a mock code if Redis is down
auth_content = auth_content.replace(
    'stored_code = redis_client.get(redis_key) if redis_client else otp_code # Mock pass if redis down for demo',
    'stored_code = redis_client.get(redis_key) if redis_client else "123456" # Mock pass if redis down for demo'
)

with open('backend/api/auth.py', 'w') as f:
    f.write(auth_content)


with open('backend/services/evidence_chain.py', 'r') as f:
    evidence_content = f.read()

# Fix undefined name 'c' and 'b' scope issue
evidence_content = evidence_content.replace(
    '{c.name: getattr(b, c.name) for b in b.__table__.columns} ',
    '{c.name: getattr(b, c.name) for c in b.__table__.columns} '
)

with open('backend/services/evidence_chain.py', 'w') as f:
    f.write(evidence_content)
