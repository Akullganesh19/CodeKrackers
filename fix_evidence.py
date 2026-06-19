import re

with open("backend/services/evidence_chain.py", "r") as f:
    content = f.read()

# Replace undefined 'c' inside list comprehension
content = content.replace(
    "{c.name: getattr(b, c.name) for b in b.__table__.columns}",
    "{col.name: getattr(b, col.name) for col in b.__table__.columns}"
)

with open("backend/services/evidence_chain.py", "w") as f:
    f.write(content)
