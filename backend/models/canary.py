"""Canary tokens for detecting database breaches and data leakage."""

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String

from backend.db.base_class import Base, TimestampMixin


class CanaryToken(Base, TimestampMixin):
    """Fake records with unique tracking identifiers - when accessed, they trigger alerts."""

    __tablename__ = "canary_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # Token tracking
    token = Column(String(64), unique=True, index=True, nullable=False)
    token_type = Column(
        String(32), nullable=False, index=True
    )  # user, threat, evidence, fir

    # Fake data that looks realistic
    fake_email = Column(String(320), nullable=True)
    fake_phone = Column(String(20), nullable=True)
    fake_ssn = Column(String(11), nullable=True)
    fake_credit_card = Column(String(19), nullable=True)
    fake_wallet_address = Column(String(42), nullable=True)
    fake_ip = Column(String(45), nullable=True)

    # Tracking metadata
    description = Column(String(256), nullable=True)  # Where this token is planted
    planted_in = Column(String(64), nullable=True, index=True)  # Which table/collection
    accessed = Column(Boolean, default=False, nullable=False, index=True)
    accessed_at = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0, nullable=False)

    # Attacker profiling
    access_ip = Column(String(45), nullable=True, index=True)
    access_user_agent = Column(String(512), nullable=True)
    access_path = Column(String(512), nullable=True)

    __table_args__ = (
        Index("ix_canary_token_accessed", "accessed", "accessed_at"),
        Index("ix_canary_type_planted", "token_type", "planted_in"),
    )

    def __repr__(self) -> str:
        return f"<CanaryToken(id={self.id}, token={self.token[:8]}..., accessed={self.accessed})>"
