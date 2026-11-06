"""
Threat Intelligence Service — aggregates signals from multiple engines.
"""
from backend.core.logger import get_logger
import logging
import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from backend.models.orm import Blacklist as BlacklistEntry, BlacklistType

logger = get_logger("vas.intel")

# ─── Known scam sender patterns (Indian context) ───
KNOWN_SCAM_SENDERS = {
    r"\+91\s?[6-9]\d{4}\s?\d{5}": 0.1,   # Indian mobile — low base
    r"AD-[A-Z]{4,6}": 0.05,                # Alpha sender (bank) — very low base
    r"\+1\d{10}": 0.4,                      # US number calling India — suspicious
    r"\+44\d{10}": 0.4,                     # UK number
    r"\+234": 0.8,                           # Nigeria — high scam signal
    r"\+86": 0.6,                            # China
}

# ─── Urgency amplifiers ───
URGENCY_PHRASES = [
    "immediately", "urgent", "within 24 hours", "right now",
    "last chance", "final notice", "account will be blocked",
    "action required", "respond immediately", "act fast",
    "turant", "jaldi", "abhi",  # Hindi urgency words
]

# ─── Impersonation targets ───
IMPERSONATION_TARGETS = [
    "rbi", "sbi", "aadhaar", "parivahan", "income tax",
    "customs", "cbi", "police", "court", "supreme court",
    "narcotics", "epfo", "uidai", "nsdl", "irctc",
    "amazon", "flipkart", "google", "microsoft", "apple",
    "fedex", "dhl", "bluedart",
]


def calculate_threat_score(
    content: str,
    sender: str,
    db: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Multi-engine threat scoring:
    1. Sender reputation
    2. Content analysis (urgency, impersonation)
    3. Blacklist lookup
    4. URL analysis
    Returns composite score 0.0–1.0 with breakdown.
    """
    content_lower = content.lower()
    scores: Dict[str, float] = {}

    # ── Engine 1: Sender Reputation ──
    sender_score = 0.0
    for pattern, base_score in KNOWN_SCAM_SENDERS.items():
        if re.search(pattern, sender):
            sender_score = max(sender_score, base_score)
    scores["sender_reputation"] = sender_score

    # ── Engine 2: Urgency Analysis ──
    urgency_hits = sum(1 for phrase in URGENCY_PHRASES if phrase in content_lower)
    scores["urgency"] = min(urgency_hits * 0.15, 1.0)

    # ── Engine 3: Impersonation Detection ──
    impersonation_hits = sum(1 for target in IMPERSONATION_TARGETS if target in content_lower)
    scores["impersonation"] = min(impersonation_hits * 0.25, 1.0)

    # ── Engine 4: URL Analysis ──
    urls = re.findall(r"https?://[^\s]+|bit\.ly/[^\s]+|tinyurl\.com/[^\s]+", content_lower)
    suspicious_tlds = [".xyz", ".tk", ".ml", ".ga", ".cf", ".top", ".buzz"]
    url_score = 0.0
    for url in urls:
        url_score += 0.3  # Any URL in SMS is suspicious
        if any(tld in url for tld in suspicious_tlds):
            url_score += 0.4
        if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", url):
            url_score += 0.5  # Raw IP in URL — very suspicious
    scores["url_analysis"] = min(url_score, 1.0)

    # ── Engine 5: Blacklist Lookup ──
    blacklist_score = 0.0
    if db:
        bl_entry = (
            db.query(BlacklistEntry)
            .filter(BlacklistEntry.value == sender, BlacklistEntry.type == BlacklistType.PHONE)
            .first()
        )
        if bl_entry:
            blacklist_score = bl_entry.confidence
            logger.warning("BLACKLIST_HIT sender=%s confidence=%.2f", sender, bl_entry.confidence)
    scores["blacklist"] = blacklist_score

    # ── Composite Score ──
    weights = {
        "sender_reputation": 0.10,
        "urgency": 0.20,
        "impersonation": 0.25,
        "url_analysis": 0.25,
        "blacklist": 0.20,
    }
    composite = sum(scores[k] * weights[k] for k in weights)

    return {
        "composite_score": round(min(composite, 1.0), 4),
        "engines": {k: round(v, 4) for k, v in scores.items()},
        "url_count": len(urls),
        "urgency_hits": urgency_hits,
        "impersonation_hits": impersonation_hits,
    }


def auto_blacklist(
    db: Session,
    identifier: str,
    identifier_type: BlacklistType,
    reason: str,
    reported_by: Optional[int] = None,
    confidence: float = 0.7,
    source: str = "ai_detection",
) -> BlacklistEntry:
    """Auto-add a scammer identifier to the blacklist."""
    existing = (
        db.query(BlacklistEntry)
        .filter(BlacklistEntry.type == identifier_type, BlacklistEntry.value == identifier)
        .first()
    )
    if existing:
        existing.report_count += 1
        existing.confidence = min(existing.confidence + 0.1, 1.0)
        db.commit()
        logger.info("BLACKLIST_UPDATED %s=%s count=%d conf=%.2f", identifier_type, identifier, existing.report_count, existing.confidence)
        return existing

    entry = BlacklistEntry(
        type=identifier_type,
        value=identifier,
        reason=reason,
        reported_by=reported_by,
        confidence=confidence,
        source=source,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    logger.warning("BLACKLIST_ADDED %s=%s conf=%.2f source=%s", identifier_type, identifier, confidence, source)
    return entry
