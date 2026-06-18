"""
Child Lock models — parental controls for calls and messages.
"""
import enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base_class import Base, TimestampMixin


class ChildLockMode(str, enum.Enum):
    OFF = "off"
    WHITELIST_ONLY = "whitelist_only"       # Only whitelisted contacts allowed
    FILTERED = "filtered"                    # Content-filtered, unknown blocked
    FULL_LOCKDOWN = "full_lockdown"          # No calls/SMS except emergency


class ChildProfile(TimestampMixin, Base):
    """Child profile linked to a parent user — controls call/SMS access."""
    __tablename__ = "child_profile"

    id = Column(Integer, primary_key=True, index=True)
    parent_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Child info
    child_name = Column(String(256), nullable=False)
    child_age = Column(Integer, nullable=True)
    device_id = Column(String(256), nullable=True)  # Linked device

    # Lock mode
    lock_mode = Column(Enum(ChildLockMode), default=ChildLockMode.FILTERED, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    pin_hash = Column(String(256), nullable=True)  # PIN to change settings

    # Call controls
    block_all_calls = Column(Boolean, default=False)
    block_unknown_calls = Column(Boolean, default=True)
    block_international_calls = Column(Boolean, default=True)
    allow_emergency_calls = Column(Boolean, default=True)   # 100, 112, 1098 always allowed

    # SMS controls
    block_all_sms = Column(Boolean, default=False)
    block_unknown_sms = Column(Boolean, default=True)
    filter_inappropriate_content = Column(Boolean, default=True)
    block_urls_in_sms = Column(Boolean, default=True)       # Block any SMS with links

    # Time restrictions
    allowed_call_start = Column(String(5), default="08:00")  # HH:MM
    allowed_call_end = Column(String(5), default="21:00")
    allowed_sms_start = Column(String(5), default="08:00")
    allowed_sms_end = Column(String(5), default="21:00")
    enforce_time_limits = Column(Boolean, default=True)

    # Whitelisted contacts (JSON array of phone numbers)
    whitelisted_contacts = Column(JSON, default=list)  # ["+91...", "+91..."]
    emergency_contacts = Column(JSON, default=list)     # Parent numbers, always allowed

    # Content filter keywords (blocked words)
    blocked_content_keywords = Column(JSON, nullable=True)

    parent = relationship("User")

    __table_args__ = (
        Index("ix_child_parent_active", "parent_id", "is_active"),
    )


class ChildActivityLog(TimestampMixin, Base):
    """Log of blocked/allowed calls and SMS for child profiles."""
    __tablename__ = "child_activity_log"

    id = Column(Integer, primary_key=True, index=True)
    child_profile_id = Column(Integer, ForeignKey("child_profile.id"), nullable=False, index=True)
    event_type = Column(String(32), nullable=False)  # call_blocked, sms_blocked, sms_filtered, call_allowed
    phone_number = Column(String(64), nullable=True)
    content_snippet = Column(String(200), nullable=True)
    reason = Column(String(256), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("ChildProfile")
