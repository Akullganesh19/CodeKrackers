"""Legal schemas with validation."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class EvidenceBase(BaseModel):
    threat_id: int
    digital_signature: str
    evidence_package_path: str
    blockchain_hash: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    pass


class Evidence(EvidenceBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


class FIRBase(BaseModel):
    threat_id: int
    status: Optional[str] = "draft"
    fir_copy_path: Optional[str] = None
    submission_id: Optional[str] = None
    legal_sections: Optional[str] = None


class FIRCreate(FIRBase):
    pass


class FIR(FIRBase):
    id: int
    reporter_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
