"""
Spam Shield Service — real-time spam call/SMS detection and auto-blocking.
Combines community reports, phone intelligence, and pattern analysis.
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models import (
    SpamReport,
    SpamFilter,
    SpamLog,
    SpamAction,
    SpamType,
    Blacklist as BlacklistEntry,
    BlacklistType,
    User,
)
from backend.services.phone_intel import analyze_phone_number
from backend.services.ai_deep_scan import ai_deep_scan
from backend.services.notifier import send_threat_alert
from backend.core.config import settings

logger = logging.getLogger("vas.spam")

# ─── Known spam patterns (Indian telecom context) ───
TELEMARKETING_PREFIXES: Tuple[str, ...] = (
    "1800",  # Toll-free (often spoofed)
    "140",  # DND category prefix
)

ROBOCALL_INDICATORS: List[str] = [
    "press 1",
    "press 2",
    "press #",
    "dial 0",
    "automated message",
    "this is a recorded",
    "do not disconnect",
]

SPAM_PATTERNS: List[str] = [
    r"(?:won|win|winner).*(?:prize|lottery|reward|crore|lakh)",
    r"(?:click|visit|open).*(?:link|url|http)",
    r"(?:otp|pin|password).*(?:share|send|verify)",
    r"(?:account|card|kyc).*(?:block|suspend|expire|deactivate)",
    r"(?:loan|credit).*(?:approved|sanction|pre-approved)",
    r"(?:job|offer|salary).*(?:apply|earn|income).*(?:lakh|month|daily)",
    r"(?:arrest|police|cbi|fir|warrant).*(?:immediately|now|urgent)",  # Added for live voice transcripts
]


def check_spam(
    db: Session,
    phone_number: str,
    user_id: int,
    spam_type: SpamType,
    content: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Multi-layer spam check with explainable scoring:
    1. Whitelist check (always allow)
    2. Community Reports & SIM Farm detection
    3. Global Blacklist lookup
    4. Phone number intelligence (VoIP, international)
    5. Content pattern matching (for SMS or live call transcripts)
    6. User filter rules
    """
    breakdown: List[Dict[str, Any]] = []
    spam_score = 0.0

    # ── Load user filter settings ──
    user_filter: Optional[SpamFilter] = (
        db.query(SpamFilter)
        .filter(SpamFilter.user_id == user_id, SpamFilter.is_active == True)
        .first()
    )

    # ── Layer 1: Whitelist ──
    if user_filter and user_filter.whitelisted_numbers:
        clean_number = re.sub(r"[\s\-()]", "", phone_number)
        for wl in user_filter.whitelisted_numbers:
            if re.sub(r"[\s\-()]", "", wl) in clean_number or clean_number in re.sub(
                r"[\s\-()]", "", wl
            ):
                breakdown.append(
                    {
                        "factor": "Whitelisted contact",
                        "points": "+0.0",
                        "type": "positive",
                    }
                )
                return _result(
                    SpamAction.ALLOW,
                    0.0,
                    breakdown,
                    user_id,
                    phone_number,
                    spam_type,
                    db,
                    content,
                )

    breakdown.append(
        {"factor": "Not on whitelist", "points": "+0.0", "type": "neutral"}
    )

    # ── Layer 2: Community Reports & SIM Farm Detection ──
    # Regular reports
    report_count = (
        db.query(SpamReport).filter(SpamReport.phone_number == phone_number).count()
    )
    if report_count >= 3:
        points = 0.25
        spam_score += points
        breakdown.append(
            {
                "factor": f"Reported by {report_count} users",
                "points": f"+{points}",
                "type": "negative",
            }
        )
    elif report_count > 0:
        points = round(report_count * 0.1, 2)
        spam_score += points
        breakdown.append(
            {
                "factor": f"Reported by {report_count} user(s)",
                "points": f"+{points}",
                "type": "negative",
            }
        )

    # SIM Farm Detection (cross-reference call frequency across users in last hour)
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    unique_users_called = (
        db.query(func.count(func.distinct(SpamLog.user_id)))
        .filter(SpamLog.phone_number == phone_number)
        .filter(SpamLog.created_at >= one_hour_ago)
        .scalar()
    )
    if unique_users_called and unique_users_called >= 50:
        points = 0.6
        spam_score += points
        breakdown.append(
            {
                "factor": f"SIM Farm detected: called {unique_users_called} users in 1hr",
                "points": f"+{points}",
                "type": "critical",
            }
        )

    # ── Layer 3: Blacklist ──
    bl = (
        db.query(BlacklistEntry)
        .filter(
            BlacklistEntry.value == phone_number,
            BlacklistEntry.type == BlacklistType.PHONE,
        )
        .first()
    )
    if bl:
        points = round(bl.confidence * 0.8, 2)
        spam_score += points
        breakdown.append(
            {
                "factor": f"Global blacklist hit (confidence: {bl.confidence:.0%})",
                "points": f"+{points}",
                "type": "critical",
            }
        )
    else:
        breakdown.append(
            {"factor": "Not on global blacklist", "points": "+0.0", "type": "positive"}
        )

    # ── Layer 4: Phone Intelligence ──
    phone_info = analyze_phone_number(phone_number)
    carrier_info = phone_info.get("carrier", {})

    if carrier_info.get("is_voip"):
        points = 0.3
        spam_score += points
        breakdown.append(
            {
                "factor": "VoIP number detected",
                "points": f"+{points}",
                "type": "negative",
            }
        )
        if user_filter and user_filter.block_voip:
            breakdown.append(
                {
                    "factor": "User filter: Block VoIP",
                    "points": "BLOCK",
                    "type": "critical",
                }
            )
            return _result(
                SpamAction.BLOCK,
                min(spam_score + 0.4, 1.0),
                breakdown,
                user_id,
                phone_number,
                spam_type,
                db,
                content,
            )

    if phone_info.get("country_code") and phone_info["country_code"] != "IN":
        points = 0.2
        spam_score += points
        breakdown.append(
            {
                "factor": f"International number ({phone_info['country_code']})",
                "points": f"+{points}",
                "type": "negative",
            }
        )
        if user_filter and user_filter.block_international:
            breakdown.append(
                {
                    "factor": "User filter: Block International",
                    "points": "BLOCK",
                    "type": "critical",
                }
            )
            return _result(
                SpamAction.BLOCK,
                min(spam_score + 0.3, 1.0),
                breakdown,
                user_id,
                phone_number,
                spam_type,
                db,
                content,
            )

    # ── Layer 5: Content Analysis (SMS & Mid-Call Live Transcripts) ──
    if content:
        content_lower = content.lower()

        # Pattern matching
        for pattern in SPAM_PATTERNS:
            if re.search(pattern, content_lower):
                points = 0.35
                spam_score += points
                breakdown.append(
                    {
                        "factor": f"Scam pattern detected: {pattern[:20]}...",
                        "points": f"+{points}",
                        "type": "negative",
                    }
                )

        # Robocall indicators
        for indicator in ROBOCALL_INDICATORS:
            if indicator in content_lower:
                points = 0.2
                spam_score += points
                breakdown.append(
                    {
                        "factor": f"Robocall indicator: '{indicator}'",
                        "points": f"+{points}",
                        "type": "negative",
                    }
                )

        # URLs
        if re.search(r"https?://|www\.|bit\.ly|tinyurl", content_lower):
            points = 0.1
            spam_score += points
            breakdown.append(
                {
                    "factor": "Unsolicited short URL detected",
                    "points": f"+{points}",
                    "type": "negative",
                }
            )

        # Urgency words
        urgency_words = ["immediately", "blocked", "urgent", "now", "arrest", "otp"]
        found_urgency = [w for w in urgency_words if w in content_lower]
        if found_urgency:
            points = 0.15
            spam_score += points
            breakdown.append(
                {
                    "factor": f"Urgency words: {', '.join(found_urgency)}",
                    "points": f"+{points}",
                    "type": "negative",
                }
            )

        # Custom keywords
        if user_filter and user_filter.blocked_keywords:
            for kw in user_filter.blocked_keywords:
                if kw.lower() in content_lower:
                    points = 0.3
                    spam_score += points
                    breakdown.append(
                        {
                            "factor": f"Custom blocked keyword: '{kw}'",
                            "points": f"+{points}",
                            "type": "negative",
                        }
                    )

        # ── Layer 5.5: AI Deep Scan (Groq Llama 3) ──
        # We trigger AI scan if the content is suspicious but not yet critical
        if 0.1 <= spam_score < 0.9:
            ai_result = ai_deep_scan(
                content, "sms" if spam_type == SpamType.SMS else "call_transcript"
            )
            if ai_result["score_increase"] > 0:
                points = ai_result["score_increase"]
                spam_score += points
                breakdown.append(
                    {
                        "factor": f"AI Deep Scan: {ai_result['reason']}",
                        "points": f"+{points}",
                        "type": "negative",
                    }
                )

    # ── Layer 6: Unknown caller check ──
    if user_filter and user_filter.block_unknown_callers and spam_type == SpamType.CALL:
        if not carrier_info.get("name") or carrier_info["name"] == "Unknown":
            points = 0.2
            spam_score += points
            breakdown.append(
                {
                    "factor": "Unknown caller blocked by filter",
                    "points": f"+{points}",
                    "type": "negative",
                }
            )

    # ── Decision ──
    spam_score = min(spam_score, 1.0)
    threshold: float = user_filter.min_spam_score_to_block if user_filter else 0.7

    if spam_score >= threshold:
        action = SpamAction.BLOCK
    elif spam_score >= 0.4:
        action = SpamAction.FLAG
    else:
        action = SpamAction.ALLOW

    # Auto-block if community reported & setting enabled
    if user_filter and user_filter.auto_block_reported_spam and report_count >= 2:
        action = SpamAction.BLOCK
        breakdown.append(
            {
                "factor": "User filter: Auto-block reported",
                "points": "BLOCK",
                "type": "critical",
            }
        )

    return _result(
        action, spam_score, breakdown, user_id, phone_number, spam_type, db, content
    )


def _result(
    action: SpamAction,
    score: float,
    breakdown: List[Dict[str, Any]],
    user_id: int,
    phone: str,
    spam_type: SpamType,
    db: Session,
    content: Optional[str] = None,
) -> Dict[str, Any]:
    """Log the result and return it with explainable breakdown."""
    # Convert breakdown to a summary reason for logging
    critical_factors = [
        b["factor"] for b in breakdown if b["type"] in ("negative", "critical")
    ]
    reason_str = " | ".join(critical_factors)[:500] if critical_factors else "Clean"

    log = SpamLog(
        user_id=user_id,
        phone_number=phone,
        spam_type=spam_type,
        spam_score=round(score, 4),
        action_taken=action,
        reason=reason_str,
        content_snippet=(content or "")[:200],
    )
    db.add(log)
    db.commit()

    if action == SpamAction.BLOCK:
        logger.warning(
            "SPAM_BLOCKED phone=%s score=%.2f reason=%s", phone, score, reason_str[:80]
        )

        # Trigger real-time notification to the user's phone
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.phone_number:
            send_threat_alert(
                phone_number=user.phone_number,
                threat_type="Smishing/Malicious SMS",
                score=score,
                original_sender=phone,
            )
    else:
        logger.info(
            "SPAM_CHECK phone=%s action=%s score=%.2f", phone, action.value, score
        )

    return {
        "action": action.value,
        "spam_score": round(score, 4),
        "reason_summary": reason_str,
        "breakdown": breakdown,
        "phone_number": phone,
        "type": spam_type.value,
    }
