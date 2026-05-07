"""Threat model with enriched metadata, indexing, and audit trail."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, JSON, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.db.base_class import Base, TimestampMixin


class ThreatType(str, enum.Enum):
    SMISHING = "smishing"
    VISHING = "vishing"
    CRYPTO_SCAM = "crypto_scam"


class ThreatSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatStatus(str, enum.Enum):
    DETECTED = "detected"
    CONFIRMED = "confirmed"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class Threat(TimestampMixin, Base):
    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(ThreatType), nullable=False, index=True)
    source_number = Column(String(64), index=True, nullable=False)
    content = Column(Text, nullable=True)  # SMS text or call transcript
    severity = Column(Enum(ThreatSeverity), default=ThreatSeverity.MEDIUM, index=True)
    status = Column(Enum(ThreatStatus), default=ThreatStatus.DETECTED, index=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata_json = Column(JSON, nullable=True)

    # Attribution
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    owner = relationship("User", back_populates="threats")

    # Evidence chain
    evidence = relationship("Evidence", back_populates="threat", uselist=False)

    # Composite indexes for common queries
    __table_args__ = (
        Index("ix_threat_type_severity", "type", "severity"),
        Index("ix_threat_timestamp_type", "timestamp", "type"),
        Index("ix_threat_owner_status", "owner_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Threat(id={self.id}, type={self.type}, severity={self.severity}, score={self.confidence_score})>"
