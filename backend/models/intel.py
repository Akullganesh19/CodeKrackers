"""
User consent and device intelligence models.
All data collection requires explicit user consent (GDPR/IT Act compliant).
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON, Index  # noqa: E501
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base_class import Base, TimestampMixin


class UserConsent(TimestampMixin, Base):
    """Tracks user consent for data collection — legally required before any gathering."""  # noqa: E501
    __tablename__ = "user_consent"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Consent flags (each must be explicitly granted)
    consent_phone_lookup = Column(Boolean, default=False, nullable=False)
    consent_device_info = Column(Boolean, default=False, nullable=False)
    consent_location = Column(Boolean, default=False, nullable=False)
    consent_sms_scan = Column(Boolean, default=False, nullable=False)
    consent_call_recording = Column(Boolean, default=False, nullable=False)

    # Metadata
    consent_given_at = Column(DateTime(timezone=True), server_default=func.now())
    consent_ip = Column(String(45), nullable=True)
    consent_user_agent = Column(String(512), nullable=True)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<UserConsent(user={self.user_id}, phone={self.consent_phone_lookup}, device={self.consent_device_info})>"  # noqa: E501


class DeviceInfo(TimestampMixin, Base):
    """Device fingerprint collected from user (with consent)."""
    __tablename__ = "device_info"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # Device
    device_model = Column(String(256), nullable=True)
    device_brand = Column(String(128), nullable=True)
    os_name = Column(String(64), nullable=True)       # Android, iOS, Windows
    os_version = Column(String(64), nullable=True)
    app_version = Column(String(32), nullable=True)

    # Network
    ip_address = Column(String(45), nullable=True)
    network_type = Column(String(32), nullable=True)   # wifi, mobile_4g, mobile_5g
    carrier_name = Column(String(128), nullable=True)
    sim_operator = Column(String(128), nullable=True)
    sim_country = Column(String(8), nullable=True)

    # Location (only if consent_location is True)
    latitude = Column(String(32), nullable=True)
    longitude = Column(String(32), nullable=True)
    city = Column(String(128), nullable=True)
    state = Column(String(128), nullable=True)

    # Browser (for web users)
    browser_name = Column(String(64), nullable=True)
    browser_version = Column(String(32), nullable=True)
    screen_resolution = Column(String(32), nullable=True)
    timezone = Column(String(64), nullable=True)
    language = Column(String(16), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_device_user_os", "user_id", "os_name"),
    )


class PhoneLookup(TimestampMixin, Base):
    """Phone number intelligence gathered via Twilio Lookup API."""
    __tablename__ = "phone_lookup"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(64), nullable=False, index=True)
    looked_up_by = Column(Integer, ForeignKey("user.id"), nullable=True)

    # Twilio Lookup results
    country_code = Column(String(8), nullable=True)
    national_format = Column(String(64), nullable=True)
    carrier_name = Column(String(256), nullable=True)
    carrier_type = Column(String(32), nullable=True)  # mobile, landline, voip, toll-free  # noqa: E501
    is_voip = Column(Boolean, default=False)           # VoIP = high scam signal
    caller_name = Column(String(256), nullable=True)

    # Risk assessment
    risk_score = Column(String(16), nullable=True)     # low, medium, high
    fraud_indicators = Column(JSON, nullable=True)

    # Linked threat (if lookup was triggered by a threat)
    threat_id = Column(Integer, ForeignKey("threat.id"), nullable=True, index=True)

    def __repr__(self) -> str:
        return f"<PhoneLookup({self.phone_number}, carrier={self.carrier_name}, voip={self.is_voip})>"  # noqa: E501
