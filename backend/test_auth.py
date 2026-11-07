import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.database import Base, engine, SessionLocal
from backend.models.orm import User, UserRole
import uuid

client = TestClient(app)

def test_registration_mass_assignment_prevented():
    test_email = f"hacker_{uuid.uuid4()}@example.com"

    try:
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_email,
                "password": "Password123!",
                "role": "super_admin"
            }
        )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        db = SessionLocal()
        user = db.query(User).filter(User.email == test_email).first()

        assert user is not None
        assert user.role == UserRole.CITIZEN, f"User role should be CITIZEN, but was {user.role}"
    finally:
        db = SessionLocal()
        user = db.query(User).filter(User.email == test_email).first()
        if user:
            db.delete(user)
            db.commit()
        db.close()
