with open("backend/services/evidence_chain.py", "r") as f:
    content = f.read()

content = content.replace(
    "{c.name: getattr(b, c.name) for c in b.__table__.columns} ",
    "{\n                    c.name: getattr(b, c.name)\n                    for c in b.__table__.columns\n                }"
)

with open("backend/services/evidence_chain.py", "w") as f:
    f.write(content)
