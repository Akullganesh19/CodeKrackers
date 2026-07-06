import uuid
from datetime import datetime
import enum
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
    func,
    Index,
    Enum,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class ThreatType(str, enum.Enum):
    vishing = "vishing"
    smishing = "smishing"
    crypto_scam = "crypto_scam"
    phishing = "phishing"
    other = "other"

    # Uppercase aliases
    VISHING = "vishing"
    SMISHING = "smishing"
    CRYPTO_SCAM = "crypto_scam"
    PHISHING = "phishing"
    OTHER = "other"


class ThreatSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"

    # Uppercase aliases
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class UserRole(str, enum.Enum):
    citizen = "citizen"
    officer = "officer"
    admin = "admin"
    super_admin = "super_admin"

    # Uppercase aliases for backward compatibility
    CITIZEN = "citizen"
    OFFICER = "officer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class FIRStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    CLOSED = "closed"


class SpamType(str, enum.Enum):
    CALL = "call"
    SMS = "sms"


class SpamAction(str, enum.Enum):
    ALLOW = "allow"
    BLOCK = "block"
    FLAG = "flag"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), unique=True)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), server_default=UserRole.CITIZEN)
    rbac_level = Column(Integer, server_default="1")
    is_active = Column(Boolean, server_default="1", default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    safety_score = Column(Float, server_default="100.0", default=100.0)
    scams_avoided = Column(Integer, server_default="0", default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    threats = relationship("Threat", back_populates="user")
    firs = relationship("FIR", back_populates="user")
    score_history = relationship("ScoreHistory", back_populates="user")


class Threat(Base):
    __tablename__ = "threats"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    type = Column(Enum(ThreatType))
    severity = Column(Enum(ThreatSeverity))
    status = Column(String(50), server_default="detected")
    raw_content = Column(Text)
    risk_score = Column(Float)
    confidence = Column(Float)
    caller_id = Column(String(20))
    sender_id = Column(String(50))
    suspicious_urls = Column(JSON)
    ipc_sections = Column(JSON)
    is_reported = Column(Boolean, server_default="0", default=False)
    detected_at = Column(DateTime, server_default=func.now())
    evidence_hash = Column(String(128))
    extra_info = Column(JSON)

    user = relationship("User", back_populates="threats")
    evidence_blocks = relationship("Evidence", back_populates="threat")
    fir = relationship("FIR", back_populates="threat", uselist=False)
    honeypot_session = relationship(
        "HoneypotSession", back_populates="threat", uselist=False
    )

    __table_args__ = (
        Index("ix_threats_caller_id_detected_at", "caller_id", "detected_at"),
    )


class Evidence(Base):
    __tablename__ = "evidence_chain"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_id = Column(String(36), ForeignKey("threats.id"))
    block_index = Column(Integer, autoincrement=True, unique=True)
    previous_hash = Column(String(128))
    current_hash = Column(String(128), unique=True)
    payload = Column(JSON)
    digital_signature = Column(String(256))
    timestamp = Column(DateTime, server_default=func.now())
    block_type = Column(String(50))

    threat = relationship("Threat", back_populates="evidence_blocks")


class FIR(Base):
    __tablename__ = "firs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_number = Column(String(50), unique=True)
    threat_id = Column(String(36), ForeignKey("threats.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    status = Column(String(50), server_default="draft")
    pdf_path = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    threat = relationship("Threat", back_populates="fir")
    user = relationship("User", back_populates="firs")


class HoneypotSession(Base):
    __tablename__ = "honeypot_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_id = Column(String(36), ForeignKey("threats.id"))
    scammer_number = Column(String(20))
    session_start = Column(DateTime, server_default=func.now())
    session_end = Column(DateTime)
    duration_seconds = Column(Integer)
    status = Column(String(50), server_default="active")
    evidence_collected = Column(JSON)

    threat = relationship("Threat", back_populates="honeypot_session")


class ScoreHistory(Base):
    __tablename__ = "score_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    score = Column(Float)
    recorded_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="score_history")


class BlacklistType(str, enum.Enum):
    PHONE = "phone"
    URL = "url"
    IP = "ip"
    WALLET = "wallet"


class Blacklist(Base):
    __tablename__ = "blacklist"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    value = Column(String(255), unique=True, index=True)  # Phone or URL
    type = Column(Enum(BlacklistType))  # PHONE, URL, IP
    reason = Column(Text)
    severity = Column(String(20), default="high")
    confidence = Column(Float, default=0.7)
    report_count = Column(Integer, default=1)
    is_verified = Column(Boolean, default=False)
    source = Column(String(100), default="ai_detection")
    added_at = Column(DateTime, server_default=func.now())


class CanaryTrap(Base):
    __tablename__ = "canary_traps"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(255), unique=True, index=True)
    token_type = Column(String(50))  # EMAIL, PHONE, URL
    fake_email = Column(String(255))
    fake_phone = Column(String(20))
    fake_ssn = Column(String(20))
    fake_credit_card = Column(String(20))
    fake_wallet_address = Column(String(100))
    fake_ip = Column(String(45))
    description = Column(Text)
    planted_in = Column(String(100))
    accessed = Column(Boolean, default=False)
    accessed_at = Column(DateTime)
    access_ip = Column(String(45))
    access_user_agent = Column(String(512))
    access_path = Column(String(512))
    access_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class ChildLockMode(str, enum.Enum):
    FULL_LOCKDOWN = "full_lockdown"
    WHITELIST_ONLY = "whitelist_only"
    MONITOR_ONLY = "monitor_only"
    OFF = "off"


class ChildProfile(Base):
    __tablename__ = "child_profiles"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("users.id"))
    child_name = Column(String(100))
    child_age = Column(Integer)
    is_active = Column(Boolean, default=True)
    lock_mode = Column(Enum(ChildLockMode), default=ChildLockMode.OFF)
    allow_emergency_calls = Column(Boolean, default=True)
    emergency_contacts = Column(JSON)  # List of numbers
    whitelisted_contacts = Column(JSON)
    block_all_calls = Column(Boolean, default=False)
    block_unknown_calls = Column(Boolean, default=True)
    block_international_calls = Column(Boolean, default=True)
    block_all_sms = Column(Boolean, default=False)
    block_unknown_sms = Column(Boolean, default=True)
    block_urls_in_sms = Column(Boolean, default=True)
    filter_inappropriate_content = Column(Boolean, default=True)
    blocked_content_keywords = Column(JSON)
    enforce_time_limits = Column(Boolean, default=True)
    allowed_call_start = Column(String(5), default="08:00")
    allowed_call_end = Column(String(5), default="21:00")
    allowed_sms_start = Column(String(5), default="08:00")
    allowed_sms_end = Column(String(5), default="21:00")
    created_at = Column(DateTime, server_default=func.now())


class ChildActivityLog(Base):
    __tablename__ = "child_activity_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_profile_id = Column(String(36), ForeignKey("child_profiles.id"))
    event_type = Column(String(50))  # call_allowed, call_blocked, sms_filtered, etc.
    phone_number = Column(String(20))
    reason = Column(String(255))
    content_snippet = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())


class IntelLog(Base):
    __tablename__ = "intel_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(100))
    threat_type = Column(String(50))
    raw_data = Column(JSON)
    reputation_score = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())


class LegalDocument(Base):
    __tablename__ = "legal_documents"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    threat_id = Column(String(36), ForeignKey("threats.id"))
    doc_type = Column(String(50))  # FIR, NOTICE, EVIDENCE_REPORT
    file_path = Column(String(512))
    sections_applied = Column(JSON)  # IPC/IT Act sections
    created_at = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(100))
    resource = Column(String(100))
    details = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    framework = Column(String(50))
    sha384_hash = Column(String(96), unique=True)
    file_size_bytes = Column(Integer)
    original_filename = Column(String(255))
    trained_by = Column(String(100))
    training_dataset = Column(String(255))
    git_commit = Column(String(40))
    accuracy = Column(Float)
    f1_score = Column(Float)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    deployed_at = Column(DateTime)
    deployment_artifact = Column(String(512))
    watermark_embedding = Column(Text)  # Storing as hex/base64 for simplicity
    watermark_verified = Column(Boolean, default=False)
    adversarial_robustness = Column(Float)
    tags = Column(JSON)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    approved_by = Column(String(100))
    approved_at = Column(DateTime)


class ModelInferenceLog(Base):
    __tablename__ = "model_inference_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_ip = Column(String(45))
    user_agent = Column(String(512))
    api_key_hash = Column(String(64))
    model_name = Column(String(100))
    model_version = Column(String(50))
    input_hash = Column(String(64))
    input_length = Column(Integer)
    response_time_ms = Column(Float)
    is_suspicious = Column(Boolean, default=False)
    suspicion_reason = Column(String(255))
    extraction_risk_score = Column(Float)
    created_at = Column(DateTime, server_default=func.now())


class UserConsent(Base):
    __tablename__ = "user_consents"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    consent_phone_lookup = Column(Boolean, default=False)
    consent_device_info = Column(Boolean, default=False)
    consent_location = Column(Boolean, default=False)
    consent_sms_scan = Column(Boolean, default=False)
    consent_call_recording = Column(Boolean, default=False)
    consent_ip = Column(String(45))
    consent_user_agent = Column(String(512))
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime)
    consent_given_at = Column(DateTime, server_default=func.now())


class PhoneLookup(Base):
    __tablename__ = "phone_lookups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), index=True)
    looked_up_by = Column(String(36), ForeignKey("users.id"))
    country_code = Column(String(5))
    national_format = Column(String(20))
    carrier_name = Column(String(100))
    carrier_type = Column(String(20))
    is_voip = Column(Boolean, default=False)
    risk_score = Column(String(20))
    fraud_indicators = Column(JSON)
    threat_id = Column(String(36), ForeignKey("threats.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class DeviceInfo(Base):
    __tablename__ = "device_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    device_model = Column(String(100))
    device_brand = Column(String(100))
    os_name = Column(String(50))
    os_version = Column(String(50))
    app_version = Column(String(50))
    ip_address = Column(String(45))
    network_type = Column(String(50))
    carrier_name = Column(String(100))
    sim_operator = Column(String(100))
    sim_country = Column(String(5))
    latitude = Column(Float)
    longitude = Column(Float)
    city = Column(String(100))
    state = Column(String(100))
    browser_name = Column(String(100))
    browser_version = Column(String(100))
    screen_resolution = Column(String(50))
    timezone = Column(String(100))
    language = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())


class SpamReport(Base):
    __tablename__ = "spam_reports"
    id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(String(36), ForeignKey("users.id"))
    phone_number = Column(String(20), index=True)
    spam_type = Column(Enum(SpamType))
    content = Column(Text)
    category = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())


class SpamFilter(Base):
    __tablename__ = "spam_filters"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    block_unknown_callers = Column(Boolean, default=True)
    block_international = Column(Boolean, default=True)
    block_voip = Column(Boolean, default=True)
    block_premium_rate = Column(Boolean, default=True)
    min_spam_score_to_block = Column(Float, default=0.7)
    auto_block_reported_spam = Column(Boolean, default=True)
    blocked_keywords = Column(JSON)
    whitelisted_numbers = Column(JSON)
    silent_block = Column(Boolean, default=False)
    auto_report_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class SpamLog(Base):
    __tablename__ = "spam_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    phone_number = Column(String(20), index=True)
    spam_type = Column(Enum(SpamType))
    spam_score = Column(Float)
    action_taken = Column(Enum(SpamAction))
    reason = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
