"""Blacklist and reputation models for threat intelligence."""

import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from backend.db.base_class import Base, TimestampMixin


class BlacklistType(str, enum.Enum):
    PHONE = "phone"
    IP = "ip"
    DOMAIN = "domain"
    WALLET = "wallet"


class BlacklistEntry(TimestampMixin, Base):
    """Community-powered blacklist of known scammer identifiers."""

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(BlacklistType), nullable=False, index=True)
    value = Column(
        String(256), nullable=False, index=True
    )  # phone number, IP, domain, or wallet address
    reason = Column(Text, nullable=True)
    reported_by = Column(Integer, nullable=True)  # user_id who reported
    report_count = Column(Integer, default=1, nullable=False)
    confidence = Column(Float, default=0.5, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    source = Column(
        String(128), default="user_report"
    )  # user_report, ai_detection, honeypot, external_feed

    __table_args__ = (Index("ix_blacklist_type_value", "type", "value", unique=True),)

    def __repr__(self) -> str:
        return f"<Blacklist({self.type}={self.value}, conf={self.confidence})>"


class ThreatIntelFeed(TimestampMixin, Base):
    """External threat intelligence feed entries."""

    __tablename__ = "threat_intel_feed"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(
        String(128), nullable=False, index=True
    )  # e.g. "honeypot.is", "cybercrime.gov.in"
    indicator_type = Column(String(64), nullable=False)  # phone, domain, ip, hash
    indicator_value = Column(String(512), nullable=False, index=True)
    threat_type = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    severity = Column(String(16), default="medium")
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
