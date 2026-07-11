import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum

# Enums for threat fields (matching SQLAlchemy model enums)
class ThreatType(str, Enum):  # noqa: E302
    SMISHING = "smishing"
    VISHING = "vishing"
    AI_VOICE = "ai_voice"
    URL_FRAUD = "url_fraud"
    OTP_FRAUD = "otp_fraud"

class ThreatSeverity(str, Enum):  # noqa: E302
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatStatus(str, Enum):  # noqa: E302
    detected = "detected"
    blocked = "blocked"
    flagged = "flagged"
    honeypot = "honeypot"
    fir_filed = "fir_filed"
    resolved = "resolved"

# Base schema for common threat attributes
class ThreatBase(BaseModel):  # noqa: E302
    user_id: uuid.UUID
    type: ThreatType
    severity: ThreatSeverity
    status: ThreatStatus = ThreatStatus.detected
    raw_content: Optional[str] = None
    risk_score: float
    confidence: Optional[float] = None
    caller_id: Optional[str] = None
    sender_id: Optional[str] = None
    suspicious_urls: Optional[List[str]] = None
    ipc_sections: Optional[List[Dict[str, str]]] = None
    is_reported: bool = False
    evidence_hash: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Schema for creating a new threat
class ThreatCreate(ThreatBase):  # noqa: E302
    pass

# Schema for returning threat details
class ThreatResponse(ThreatBase):  # noqa: E302
    id: uuid.UUID
    detected_at: datetime  # noqa: W292
