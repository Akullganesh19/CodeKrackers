"""User model with RBAC, audit fields, and security constraints."""
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.db.base_class import Base, TimestampMixin


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    BANK = "bank"
    OFFICER = "officer"
    ADMIN = "admin"
    SUPER_ADMIN = "superadmin"


class User(TimestampMixin, Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(256), index=True, nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    hashed_password = Column(String(1024), nullable=False)
    is_active = Column(Boolean(), default=True, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN, nullable=False, index=True)

    # Security tracking
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    threats = relationship("Threat", back_populates="owner", lazy="dynamic")
    firs = relationship("FIR", back_populates="reporter", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
