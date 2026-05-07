"""Threat schemas with validation."""
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.threat import ThreatSeverity, ThreatType


class ThreatBase(BaseModel):
    type: ThreatType
    source_number: str = Field(..., min_length=1, max_length=64)
    content: str = Field(..., max_length=10000)
    severity: Optional[ThreatSeverity] = ThreatSeverity.MEDIUM
    confidence_score: Optional[float] = Field(0.0, ge=0.0, le=1.0)
    metadata_json: Optional[Dict[str, Any]] = None


class ThreatCreate(ThreatBase):
    pass


class ThreatUpdate(BaseModel):
    severity: Optional[ThreatSeverity] = None
    status: Optional[str] = None


class ThreatInDBBase(ThreatBase):
    id: int
    timestamp: datetime
    owner_id: int
    model_config = ConfigDict(from_attributes=True)


class Threat(ThreatInDBBase):
    pass
