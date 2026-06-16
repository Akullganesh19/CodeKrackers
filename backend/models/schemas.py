from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)

class UserSchema(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str
    model_config = ConfigDict(from_attributes=True)

class ThreatCreate(BaseModel):
    type: str
    source_number: str
    content: str
    severity: str = "medium"
    confidence_score: float = 0.0

class ThreatSchema(BaseModel):
    id: str
    type: str
    source_number: Optional[str] = None
    content: Optional[str] = None
    severity: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FIRCreate(BaseModel):
    threat_id: str
    status: str = "draft"
    legal_sections: Optional[str] = None

class FIRSchema(BaseModel):
    id: str
    threat_id: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
