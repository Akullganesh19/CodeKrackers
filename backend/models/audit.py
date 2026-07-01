"""Audit log model for forensic-grade event tracking."""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.sql import func

from backend.db.base_class import Base


class AuditLog(Base):
    """Immutable audit trail for all security-sensitive events."""

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Who
    user_id = Column(Integer, nullable=True, index=True)
    user_email = Column(String(320), nullable=True)
    ip_address = Column(String(45), nullable=False)  # IPv6-safe
    user_agent = Column(String(512), nullable=True)

    # What
    action = Column(
        String(64), nullable=False, index=True
    )  # LOGIN_SUCCESS, THREAT_CREATED, FIR_GENERATED, etc.
    resource_type = Column(String(64), nullable=True)  # user, threat, fir, evidence
    resource_id = Column(Integer, nullable=True)

    # Details
    details = Column(JSON, nullable=True)
    severity = Column(String(16), default="info")  # info, warning, critical

    __table_args__ = (
        Index("ix_audit_action_timestamp", "action", "timestamp"),
        Index("ix_audit_user_action", "user_id", "action"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.user_id})>"
