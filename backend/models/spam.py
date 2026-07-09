"""
Spam Shield models — real-time spam call/SMS detection and auto-blocking.
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, JSON, Text, Index, Enum  # noqa: E501
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.db.base_class import Base, TimestampMixin


class SpamAction(str, enum.Enum):
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"          # Flag for review
    QUARANTINE = "quarantine"  # Hold for manual approval


class SpamType(str, enum.Enum):
    CALL = "call"
    SMS = "sms"


class SpamReport(TimestampMixin, Base):
    """Community-reported spam calls/SMS."""
    __tablename__ = "spam_report"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    phone_number = Column(String(64), nullable=False, index=True)
    spam_type = Column(Enum(SpamType), nullable=False)
    content = Column(Text, nullable=True)          # SMS text or call description
    category = Column(String(64), nullable=True)   # telemarketing, fraud, robocall, etc.  # noqa: E501
    is_verified = Column(Boolean, default=False)

    reporter = relationship("User")

    __table_args__ = (
        Index("ix_spam_phone_type", "phone_number", "spam_type"),
    )


class SpamFilter(TimestampMixin, Base):
    """User-configurable spam filtering rules."""
    __tablename__ = "spam_filter"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Filter settings
    is_active = Column(Boolean, default=True, nullable=False)
    block_unknown_callers = Column(Boolean, default=False)
    block_international = Column(Boolean, default=False)
    block_voip = Column(Boolean, default=True)
    block_premium_rate = Column(Boolean, default=True)
    min_spam_score_to_block = Column(Float, default=0.7)  # 0.0-1.0

    # Auto-actions
    auto_block_reported_spam = Column(Boolean, default=True)
    auto_report_blocked = Column(Boolean, default=False)
    silent_block = Column(Boolean, default=True)  # Block without ringing

    # Custom keyword filters for SMS
    blocked_keywords = Column(JSON, nullable=True)  # ["lottery", "prize", "otp"]
    whitelisted_numbers = Column(JSON, nullable=True)  # Always allow these

    user = relationship("User")


class SpamLog(TimestampMixin, Base):
    """Log of every spam check performed — forensic record."""
    __tablename__ = "spam_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    phone_number = Column(String(64), nullable=False, index=True)
    spam_type = Column(Enum(SpamType), nullable=False)
    spam_score = Column(Float, nullable=False, default=0.0)
    action_taken = Column(Enum(SpamAction), nullable=False)
    reason = Column(Text, nullable=True)
    content_snippet = Column(String(200), nullable=True)

    __table_args__ = (
        Index("ix_spamlog_user_time", "user_id", "created_at"),
    )
