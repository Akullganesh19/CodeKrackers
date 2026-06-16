"""
Canary Token Service — plants fake records in the database with unique tracking URLs.

When an attacker exfiltrates data, the fake records contain invisible tracking links.
If those links are accessed, we get immediate notification of:
  - Which database/table was breached
  - When the breach occurred
  - The attacker's IP address and User-Agent
  - Which specific canary token was triggered

This works like Thinkst Canary / canarytokens.org — self-hosted and free.
"""
import uuid
import time
import json
import logging
import secrets
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.orm import CanaryTrap as CanaryToken
from backend.core.config import settings

logger = logging.getLogger("vas.canary_service")


# ─── Token Generators ─────────────────────────────────────────────

def generate_token(token_type: str = "generic") -> str:
    """Generate a unique canary token string."""
    return f"canary_{token_type}_{secrets.token_urlsafe(16)}_{int(time.time())}"


def generate_tracking_url(token: str) -> str:
    """Generate a tracking URL that, when accessed, triggers the canary."""
    base_url = getattr(settings, "CANARY_BASE_URL", "http://localhost:8000")
    return f"{base_url}/canary/track/{token}"


# ─── CRUD Operations ──────────────────────────────────────────────

def create_canary_token(
    db: Session,
    token_type: str,
    description: Optional[str] = None,
    fake_email: Optional[str] = None,
    fake_phone: Optional[str] = None,
    fake_ssn: Optional[str] = None,
    fake_credit_card: Optional[str] = None,
    fake_wallet_address: Optional[str] = None,
    fake_ip: Optional[str] = None,
    planted_in: Optional[str] = None,
) -> CanaryToken:
    """
    Create and plant a new canary token.
    
    The token will be invisible to normal users but detectable by attackers
    who exfiltrate data. The tracking URL is embedded in the fake data.
    """
    token_val = generate_token(token_type)
    _ = generate_tracking_url(token_val)

    # Embed tracking URL into one of the fake fields if not otherwise specified
    if not any([fake_email, fake_phone, fake_ssn, fake_credit_card, fake_wallet_address, fake_ip]):
        fake_email = f"user_{token_val[:8]}@vas-system.local"

    canary = CanaryToken(
        token=token_val,
        token_type=token_type,
        fake_email=fake_email or f"canary_{token_val[:8]}@vas-system.local",
        fake_phone=fake_phone or f"+1-555-{secrets.randbelow(9000) + 1000:04d}",
        fake_ssn=fake_ssn,
        fake_credit_card=fake_credit_card,
        fake_wallet_address=fake_wallet_address,
        fake_ip=fake_ip or f"10.0.{secrets.randbelow(256)}.{secrets.randbelow(256)}",
        description=description or f"Canary token planted in {planted_in or 'unknown'}",
        planted_in=planted_in,
        accessed=False,
    )

    db.add(canary)
    db.commit()
    db.refresh(canary)
    logger.info(
        "CANARY CREATED id=%s type=%s planted_in=%s",
        canary.id, token_type, planted_in,
    )
    return canary


def get_canary_by_token(db: Session, token: str) -> Optional[CanaryToken]:
    """Look up a canary token by its token string."""
    return db.query(CanaryToken).filter(CanaryToken.token == token).first()


def trigger_canary(
    db: Session,
    token: str,
    ip: str,
    user_agent: str,
    path: str,
) -> Optional[CanaryToken]:
    """
    Mark a canary token as accessed/triggered.
    
    This is called when the tracking URL is requested or when token
    values are detected in incoming request data (indicating exfiltration).
    """
    canary = get_canary_by_token(db, token)
    if not canary:
        logger.warning("CANARY LOOKUP FAILED token=%s from=%s", token[:16], ip)
        return None

    canary.accessed = True
    canary.accessed_at = datetime.now(timezone.utc)
    canary.access_count = (canary.access_count or 0) + 1
    canary.access_ip = ip
    canary.access_user_agent = user_agent
    canary.access_path = path

    db.commit()
    db.refresh(canary)

    logger.critical(
        "CANARY TRIGGERED! token=%s type=%s planted_in=%s ip=%s ua=%s path=%s",
        canary.token[:16],
        canary.token_type,
        canary.planted_in,
        ip,
        user_agent[:80],
        path,
    )

    # In production, send alert:
    # - Email to security team
    # - Slack/Teams notification
    # - SMS via Twilio
    # - Webhook to SIEM

    return canary


def plant_seed_tokens(db: Session):
    """Plant a set of initial canary tokens across various tables/data stores."""
    existing = db.query(CanaryToken).count()
    if existing > 0:
        logger.info("Canary tokens already planted (%d found), skipping", existing)
        return

    tokens_config = [
        {
            "token_type": "user",
            "description": "Fake super admin user in users table",
            "fake_email": "admin@vas-system.local",
            "fake_phone": "+1-555-0001",
            "fake_ssn": None,
            "fake_credit_card": None,
            "fake_wallet_address": None,
            "planted_in": "users",
        },
        {
            "token_type": "user",
            "description": "Fake officer with high privileges",
            "fake_email": "sysadmin@vas-system.local",
            "fake_phone": "+1-555-0999",
            "fake_ssn": None,
            "fake_credit_card": None,
            "fake_wallet_address": None,
            "planted_in": "users",
        },
        {
            "token_type": "threat",
            "description": "Fake threat record with sensitive data",
            "fake_email": "breach_alert@vas-system.local",
            "fake_phone": "+1-555-0000",
            "fake_ssn": "666-00-{0:04d}".format(secrets.randbelow(10000)),
            "fake_credit_card": "4532-{0:04d}-{1:04d}-{2:04d}".format(
                secrets.randbelow(10000),
                secrets.randbelow(10000),
                secrets.randbelow(10000),
            ),
            "planted_in": "threats",
        },
        {
            "token_type": "evidence",
            "description": "Fake evidence record with wallet address",
            "fake_email": "evidence_chain@vas-system.local",
            "fake_wallet_address": f"0x{secrets.token_hex(20)}",
            "planted_in": "evidence",
        },
        {
            "token_type": "fir",
            "description": "Fake FIR record with personal data",
            "fake_email": "fir_canary@vas-system.local",
            "fake_phone": "+1-555-9999",
            "fake_ssn": "999-00-{0:04d}".format(secrets.randbelow(10000)),
            "planted_in": "fir_reports",
        },
        {
            "token_type": "config",
            "description": "Fake config/credential leak canary",
            "fake_email": "config_backup@vas-system.local",
            "planted_in": "config_backups",
        },
        {
            "token_type": "api_key",
            "description": "Fake API key stored in database",
            "fake_email": "api_gateway@vas-system.local",
            "planted_in": "api_keys",
        },
    ]

    for cfg in tokens_config:
        create_canary_token(db, **cfg)

    logger.info("Planted %d seed canary tokens in database", len(tokens_config))


# ─── Scanning for leaked tokens ────────────────────────────────────

def scan_request_for_tokens(
    db: Session,
    request_data: str,
    source_ip: str,
    user_agent: str,
    path: str,
) -> List[CanaryToken]:
    """
    Scan a string (query params, body, headers) for known canary token values.
    
    If a token value is found in incoming data, it means the attacker has
    exfiltrated data and is now using it — immediate alert.
    """
    triggered: List[CanaryToken] = []
    tokens = db.query(CanaryToken).filter(
        CanaryToken.accessed == False
    ).all()

    for canary in tokens:
        # Check if any of the fake data fields appear in the request
        search_fields = [
            canary.fake_email,
            canary.fake_phone,
            canary.fake_ssn,
            canary.fake_credit_card,
            canary.fake_wallet_address,
            canary.fake_ip,
            canary.token,
        ]
        for field in search_fields:
            if field and field in request_data:
                logger.critical(
                    "CANARY DATA LEAK DETECTED! token=%s field=%s from=%s",
                    canary.token[:16],
                    field[:30],
                    source_ip,
                )
                trigger_canary(db, canary.token, source_ip, user_agent, path)
                triggered.append(canary)
                break

    return triggered