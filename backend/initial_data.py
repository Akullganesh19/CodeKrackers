"""
Database seed script with realistic Indian cybercrime threat data.
"""

from datetime import datetime, timedelta, timezone

from backend.core import security
from backend.db.base import Base
from backend.db.session import SessionLocal, engine
from backend.models.legal import Evidence, FIR
from backend.models.threat import Threat, ThreatSeverity, ThreatType
from backend.models.user import User, UserRole


def init_db() -> None:
    """Initialize the database with schema and seed data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    now = datetime.now(timezone.utc)

    # ─── Users ───
    admin = db.query(User).filter(User.email == "admin@vas.ai").first()
    if not admin:
        admin = User(
            email="admin@vas.ai",
            hashed_password=security.get_password_hash("Admin@123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    officer = db.query(User).filter(User.email == "officer@cybercrime.gov.in").first()
    if not officer:
        officer = User(
            email="officer@cybercrime.gov.in",
            hashed_password=security.get_password_hash("Officer@123"),
            full_name="Inspector Rajesh Kumar",
            role=UserRole.OFFICER,
        )
        db.add(officer)
        db.commit()

    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = User(
            email="user@example.com",
            hashed_password=security.get_password_hash("User@1234"),
            full_name="Anirudh Sharma",
            role=UserRole.CITIZEN,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # ─── Threats ───
    if db.query(Threat).count() == 0:
        threats = [
            Threat(
                type=ThreatType.SMISHING,
                source_number="+91 98765 43210",
                content="Your PARIVAHAN challan is due. Pay immediately at http://parivahan-gov.in.scam/pay",
                severity=ThreatSeverity.CRITICAL,
                confidence_score=0.98,
                owner_id=user.id,
                timestamp=now - timedelta(hours=2),
                metadata_json={"ai_category": "phishing", "keyword_hits": 3},
            ),
            Threat(
                type=ThreatType.VISHING,
                source_number="+91 12345 67890",
                content="TRANSCRIPT: This is CBI calling. Your son is in custody. Send 50k to bail him out...",
                severity=ThreatSeverity.HIGH,
                confidence_score=0.85,
                owner_id=user.id,
                timestamp=now - timedelta(days=1),
                metadata_json={"ai_category": "impersonation", "keyword_hits": 2},
            ),
            Threat(
                type=ThreatType.SMISHING,
                source_number="AD-KOTAKB",
                content="Dear customer, your KYC has expired. Update now to avoid account block: bit.ly/update-kyc-now",
                severity=ThreatSeverity.HIGH,
                confidence_score=0.92,
                owner_id=user.id,
                timestamp=now - timedelta(minutes=45),
                metadata_json={
                    "ai_category": "otp_theft",
                    "keyword_hits": 4,
                    "url_hits": 1,
                },
            ),
            Threat(
                type=ThreatType.SMISHING,
                source_number="+91 77889 00112",
                content="Congratulations! You won Rs 25,00,000 in Amazon Lucky Draw. Claim now: http://amaz0n-prize.xyz/claim",
                severity=ThreatSeverity.CRITICAL,
                confidence_score=0.97,
                owner_id=user.id,
                timestamp=now - timedelta(hours=5),
                metadata_json={
                    "ai_category": "financial_fraud",
                    "keyword_hits": 3,
                    "url_hits": 2,
                },
            ),
            Threat(
                type=ThreatType.VISHING,
                source_number="+91 99887 66554",
                content="TRANSCRIPT: Sir, I'm calling from SBI. Your account will be blocked in 30 minutes unless you verify your Aadhaar...",
                severity=ThreatSeverity.HIGH,
                confidence_score=0.89,
                owner_id=user.id,
                timestamp=now - timedelta(hours=8),
                metadata_json={"ai_category": "impersonation", "keyword_hits": 3},
            ),
        ]
        db.add_all(threats)
        db.commit()

    db.close()
    print("[OK] Database initialized with seed data.")
    print("   Admin:   admin@vas.ai / Admin@123")
    print("   Officer: officer@cybercrime.gov.in / Officer@123")
    print("   User:    user@example.com / User@1234")


if __name__ == "__main__":
    init_db()
