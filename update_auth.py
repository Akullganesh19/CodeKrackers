import re

auth_file = "backend/api/auth.py"
with open(auth_file, "r") as f:
    content = f.read()

import_statement = "from backend.core.events.bus import event_bus\n"

if "from backend.core.events.bus import event_bus" not in content:
    content = content.replace("from pydantic import BaseModel", "from pydantic import BaseModel\n" + import_statement)

# Now we need to inject the event bus emit at the bottom of login_access_token_password
login_target = """
    role_val = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token(subject=str(user.id), role=role_val, expires_delta=access_token_expires)

    # SYNAPSE: Emit login event for Analytics to consume asynchronously
    event_bus.emit("user.login", {
        "user_id": str(user.id),
        "email": user.email,
        "ip_address": request.client.host if request.client else "unknown"
    })

    return {"""

content = re.sub(
    r"    role_val = user.role.value if hasattr\(user.role, 'value'\) else str\(user.role\)\n    access_token_expires = timedelta\(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES\)\n    token = security.create_access_token\(subject=str\(user.id\), role=role_val, expires_delta=access_token_expires\)\n\n    return \{",
    login_target,
    content
)

with open(auth_file, "w") as f:
    f.write(content)
