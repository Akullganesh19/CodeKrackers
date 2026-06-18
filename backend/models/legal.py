"""Legal models: Evidence chain and FIR with full audit trail."""
import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base_class import Base, TimestampMixin


class EvidenceType(str, enum.Enum):
    SMS_CAPTURE = "sms_capture"
    CALL_RECORDING = "call_recording"
    TRANSCRIPT = "transcript"
    SCREENSHOT = "screenshot"
    METADATA = "metadata"


class FIRStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"


class Evidence(TimestampMixin, Base):
    id = Column(Integer, primary_key=True, index=True)
    threat_id = Column(Integer, ForeignKey("threat.id"), nullable=False, index=True)
    evidence_type = Column(Enum(EvidenceType), default=EvidenceType.METADATA)
    digital_signature = Column(String(512), nullable=False)
    evidence_package_path = Column(String(1024), nullable=True)
    blockchain_hash = Column(String(128), nullable=True, index=True)
    sha256_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Chain of custody
    collected_by = Column(String(256), nullable=True)
    notes = Column(Text, nullable=True)

    threat = relationship("Threat", back_populates="evidence")

    def __repr__(self) -> str:
        return f"<Evidence(id={self.id}, threat_id={self.threat_id}, type={self.evidence_type})>"


class FIR(TimestampMixin, Base):
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    threat_id = Column(Integer, ForeignKey("threat.id"), nullable=False, index=True)
    status = Column(Enum(FIRStatus), default=FIRStatus.DRAFT, index=True)
    fir_copy_path = Column(String(1024), nullable=True)
    submission_id = Column(String(128), nullable=True, unique=True)
    assigned_officer = Column(String(256), nullable=True)
    legal_sections = Column(Text, nullable=True)  # Comma-separated IPC/IT Act sections

    reporter = relationship("User", back_populates="firs")
    threat = relationship("Threat")

    __table_args__ = (
        Index("ix_fir_status_reporter", "status", "reporter_id"),
    )

    def __repr__(self) -> str:
        return f"<FIR(id={self.id}, status={self.status}, threat_id={self.threat_id})>"
