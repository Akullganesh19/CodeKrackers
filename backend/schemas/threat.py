"""Threat schemas with validation."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models import ThreatSeverity, ThreatType


class ThreatBase(BaseModel):
    type: ThreatType
    sender_id: str = Field(..., min_length=1, max_length=64)
    raw_content: str = Field(..., max_length=10000)
    severity: Optional[ThreatSeverity] = ThreatSeverity.MEDIUM
    confidence: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    extra_info: Optional[Dict[str, Any]] = None


class ThreatCreate(ThreatBase):
    pass


class ThreatUpdate(BaseModel):
    severity: Optional[ThreatSeverity] = None
    status: Optional[str] = None


class ThreatInDBBase(ThreatBase):
    id: str
    detected_at: datetime
    user_id: str
    model_config = ConfigDict(from_attributes=True)


class Threat(ThreatInDBBase):
    pass
