import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Enums for threat fields (matching SQLAlchemy model enums)


class ThreatType(str, Enum):
    SMISHING = "smishing"
    VISHING = "vishing"
    AI_VOICE = "ai_voice"
    URL_FRAUD = "url_fraud"
    OTP_FRAUD = "otp_fraud"


class ThreatSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatStatus(str, Enum):
    detected = "detected"
    blocked = "blocked"
    flagged = "flagged"
    honeypot = "honeypot"
    fir_filed = "fir_filed"
    resolved = "resolved"


# Base schema for common threat attributes


class ThreatBase(BaseModel):
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


class ThreatCreate(ThreatBase):
    pass


# Schema for returning threat details


class ThreatResponse(ThreatBase):
    id: uuid.UUID
    detected_at: datetime
