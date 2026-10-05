import re

with open("backend/services/evidence_chain.py", "r") as f:
    content = f.read()

# Fix undefined name 'c' and 'b' in package_evidence
old = """            "incident": {c.name: getattr(threat, c.name) for c in threat.__table__.columns},
            "fir_filing": {c.name: getattr(fir, c.name) for c in fir.__table__.columns} if fir else None,
            "blockchain_audit_trail": [
                {c.name: getattr(b, c.name) for b in b.__table__.columns}
                for b in blocks
            ]"""

new = """            "incident": {c.name: getattr(threat, c.name) for c in threat.__table__.columns},
            "fir_filing": {c.name: getattr(fir, c.name) for c in fir.__table__.columns} if fir else None,
            "blockchain_audit_trail": [
                {c.name: getattr(b, c.name) for c in b.__table__.columns}
                for b in blocks
            ]"""

content = content.replace(old, new)
with open("backend/services/evidence_chain.py", "w") as f:
    f.write(content)
