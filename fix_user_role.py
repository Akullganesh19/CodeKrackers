import re

with open("backend/schemas/user.py", "r") as f:
    content = f.read()
content = content.replace("role: Optional[UserRole] = UserRole.USER", "role: Optional[UserRole] = UserRole.CITIZEN")
with open("backend/schemas/user.py", "w") as f:
    f.write(content)

with open("backend/models/user.py", "r") as f:
    content = f.read()
content = content.replace('CITIZEN = "citizen"\n    USER = "user"', 'CITIZEN = "citizen"\n    USER = "citizen"')
with open("backend/models/user.py", "w") as f:
    f.write(content)
