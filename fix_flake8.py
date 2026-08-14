import re
import sys

def fix_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Fix backend/api/auth.py:117:68: F821 undefined name 'otp_code'
    if 'backend/api/auth.py' in filepath:
        content = content.replace("stored_code = redis_client.get(redis_key) if redis_client else otp_code # Mock pass if redis down for demo", "stored_code = redis_client.get(redis_key) if redis_client else request.otp_code # Mock pass if redis down for demo")

    # Fix backend/services/evidence_chain.py:172: F821 undefined name 'c'
    if 'backend/services/evidence_chain.py' in filepath:
        content = re.sub(
            r'\{c\.name: getattr\(b, c\.name\) for b in b\.__table__\.columns\}',
            r'{c.name: getattr(b, c.name) for c in b.__table__.columns}',
            content
        )

    with open(filepath, 'w') as f:
        f.write(content)

fix_file('backend/api/auth.py')
fix_file('backend/services/evidence_chain.py')
