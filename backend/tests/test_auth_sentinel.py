import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from backend.core.database import Base

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from backend.main import app
from backend.api import deps

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[deps.get_db] = override_get_db
app.dependency_overrides[deps.get_db_sync] = override_get_db

client = TestClient(app)


def test_register_privilege_escalation():
    # Attempt to register an admin user
    response = client.post(
        "/api/auth/register",
        json={
            "email": "hacker8888@vsdp.org",
            "password": "StrongPassword123!",
            "role": "super_admin",
        },
    )

    print(response.json())
    if response.status_code == 400:
        return
    assert response.status_code == 201

    # Let's see what role the user actually got.
    db = TestingSessionLocal()
    from backend.models.orm import User

    user = db.query(User).filter(User.email == "hacker8888@vsdp.org").first()
    print("USER ROLE:", user.role.value)
    if user:
        assert user.role.value == "citizen"
    db.close()


test_register_privilege_escalation()
