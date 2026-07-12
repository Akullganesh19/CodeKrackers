"""Honeypot endpoint access tracking for attacker profiling."""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index, Boolean
from sqlalchemy.sql import func

from backend.db.base_class import Base


class HoneypotAccess(Base):
    """Immutable log of all honeypot endpoint access attempts."""

    __tablename__ = "honeypot_access"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Attacker identity
    ip_address = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(512), nullable=True)
    x_forwarded_for = Column(String(255), nullable=True)

    # Honeypot endpoint details
    endpoint = Column(
        String(256), nullable=False, index=True
    )  # /api/admin/export-users
    method = Column(String(16), nullable=False)

    # Request analysis
    query_params = Column(JSON, nullable=True)  # Key-value pairs
    headers = Column(JSON, nullable=True)  # Selected headers only
    body_preview = Column(String(512), nullable=True)  # First 512 chars of body

    # Attacker behavior profiling
    is_authenticated = Column(Boolean, default=False, nullable=False, index=True)
    auth_type = Column(String(32), nullable=True)  # bearer, basic, cookie
    requested_role = Column(String(32), nullable=True)  # If trying to access admin

    # Threat intelligence
    threat_indicators = Column(JSON, nullable=True)  # List of suspicious patterns found
    risk_score = Column(Integer, default=0, nullable=False, index=True)  # 0-100

    __table_args__ = (
        Index("ix_honeypot_ip_endpoint", "ip_address", "endpoint"),
        Index("ix_honeypot_timestamp_risk", "timestamp", "risk_score"),
    )

    def __repr__(self) -> str:
        return f"<HoneypotAccess(id={self.id}, endpoint={self.endpoint}, ip={self.ip_address})>"
