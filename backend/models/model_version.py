"""Model versioning with checksum verification to prevent supply chain poisoning."""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.sql import func

from backend.db.base_class import Base, TimestampMixin


class ModelVersion(Base, TimestampMixin):
    """
    Track every deployed model version with cryptographic checksums.
    
    Prevents supply chain attacks where model weights are poisoned.
    Every model is registered with SHA-384 hash, source info, and
    a signed manifest before deployment.
    """
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Model identity
    name = Column(String(128), nullable=False, index=True)  # e.g., "smishing-bert", "voice-rawnet2"
    version = Column(String(32), nullable=False, index=True)  # semver: "1.2.3"
    framework = Column(String(32), nullable=False)  # transformers, pytorch, sklearn
    
    # Checksum verification
    sha384_hash = Column(String(96), nullable=False)  # SHA-384 hex digest of model weights
    file_size_bytes = Column(Integer, nullable=False)
    original_filename = Column(String(256), nullable=True)
    
    # Provenance
    trained_by = Column(String(128), nullable=True)  # User/email who trained
    training_dataset = Column(String(256), nullable=True)
    training_date = Column(DateTime(timezone=True), nullable=True)
    git_commit = Column(String(64), nullable=True)  # Git hash of training code
    
    # Safety & security
    is_approved = Column(Boolean, default=False, nullable=False, index=True)
    approved_by = Column(String(128), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Quality metrics
    accuracy = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    adversarial_robustness = Column(Float, nullable=True)  # Robustness score against ART attacks
    
    # Metadata
    tags = Column(JSON, nullable=True)  # {"purpose": "smishing_detection", "language": "en"}
    notes = Column(Text, nullable=True)
    
    # Watermark
    watermark_embedding = Column(LargeBinary, nullable=True)  # Serialized watermark fingerprint
    watermark_verified = Column(Boolean, default=False, nullable=False)
    
    # Deployment
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    deployment_artifact = Column(String(512), nullable=True)  # Path/URL to weights file
    
    __table_args__ = (
        Index("ix_model_version_active", "name", "is_active"),
        Index("ix_model_name_version", "name", "version", unique=True),
    )

    def __repr__(self):
        return f"<ModelVersion(name={self.name}, v={self.version}, approved={self.is_approved})>"


class ModelInferenceLog(Base, TimestampMixin):
    """
    Log every inference API call for model extraction detection.
    
    Analyzed to detect model stealing attempts:
    - >50 identical-structure queries/min = likely model extraction
    - Unusual input distributions = probing for vulnerabilities
    """
    __tablename__ = "model_inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Request identity
    client_ip = Column(String(45), nullable=False, index=True)
    user_agent = Column(String(256), nullable=True)
    api_key_hash = Column(String(64), nullable=True, index=True)
    
    # Model info
    model_name = Column(String(128), nullable=False, index=True)
    model_version = Column(String(32), nullable=True)
    
    # Request details
    input_hash = Column(String(64), nullable=True)  # SHA-256 of input (privacy-safe)
    input_length = Column(Integer, nullable=True)  # Number of tokens/characters
    response_time_ms = Column(Float, nullable=True)
    
    # Security
    is_suspicious = Column(Boolean, default=False, nullable=False, index=True)
    suspicion_reason = Column(String(256), nullable=True)
    extraction_risk_score = Column(Float, default=0.0, nullable=False)
    
    __table_args__ = (
        Index("ix_inference_ip_model", "client_ip", "model_name"),
        Index("ix_inference_timestamp", "created_at"),
    )

    def __repr__(self):
        return f"<InferenceLog(model={self.model_name}, ip={self.client_ip}, suspicious={self.is_suspicious})>"