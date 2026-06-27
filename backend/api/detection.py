"""
Threat detection endpoints powered by Groq Llama 3 + Crypto Honeypot verification.
"""
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models import User
from backend.schemas.threat import ThreatCreate, Threat as ThreatSchema
from backend.api.v1.endpoints.threats import create_threat
from backend.core.config import settings
from backend.utils.ai import client
from backend.utils.crypto import extract_crypto_addresses, check_crypto_honeypot

logger = logging.getLogger("vas.detection")
router = APIRouter()

# ─── Scam keyword database (Indian context) ───
SCAM_KEYWORDS = [
    "kyc", "challan", "otp", "blocked", "suspended", "verify",
    "parivahan", "aadhaar", "pan card", "income tax", "epfo",
    "sbi", "rbi", "customs", "courier", "fedex", "arrest",
    "warrant", "cbi", "narcotics", "money laundering",
    "click here", "update now", "expir", "urgent", "immediately",
    "bit.ly", "tinyurl", "prize", "lottery", "won", "reward",
]

SCAM_URL_PATTERNS = [
    "bit.ly", "tinyurl", "t.co", "goo.gl", "is.gd",
    ".xyz", ".tk", ".ml", ".ga", ".cf",
    "login-secure", "verify-account", "update-kyc",
]


@router.post("/sms", response_model=ThreatSchema)
async def detect_sms(
    *,
    db: Session = Depends(deps.get_db),
    sms_data: dict,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """AI-powered SMS threat detection with multi-layer analysis."""
    content = sms_data.get("body", "")
    sender = sms_data.get("sender", "")
    content_lower = content.lower()

    logger.info("SMS scan request from user=%d sender=%s", current_user.id, sender[:20])

    # Layer 1: Groq AI Analysis
    ai_analysis = {"is_scam": False, "confidence": 0, "reason": ""}
    if client:
        try:
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a cybersecurity expert specializing in Indian "
                            "Smishing/Vishing attacks. Analyze the following SMS. "
                            'Return JSON: {"is_scam": bool, "confidence": float 0-1, '
                            '"reason": "brief explanation", "category": "phishing|otp_theft|impersonation|financial_fraud|safe"}'
                        ),
                    },
                    {"role": "user", "content": f"Sender: {sender}\nBody: {content}"},
                ],
                response_format={"type": "json_object"},
            )
            ai_analysis = json.loads(completion.choices[0].message.content)
            logger.info("Groq analysis: scam=%s conf=%.2f", ai_analysis.get("is_scam"), ai_analysis.get("confidence", 0))
        except Exception as e:
            logger.error("Groq analysis failed: %s", e)

    # Layer 2: Keyword matching
    keyword_score = sum(1 for kw in SCAM_KEYWORDS if kw in content_lower)
    url_score = sum(1 for p in SCAM_URL_PATTERNS if p in content_lower)
    keyword_confidence = min((keyword_score * 0.15) + (url_score * 0.2), 1.0)

    # Layer 3: Crypto address scanning
    crypto_addresses = extract_crypto_addresses(content)
    crypto_results = []
    for addr in crypto_addresses:
        try:
            res = await check_crypto_honeypot(addr)
            crypto_results.append({"address": addr, "analysis": res})
        except Exception as e:
            logger.error("Crypto honeypot analysis failed for %s: %s", addr, e)
            # Fallback gracefully
            crypto_results.append({"address": addr, "analysis": {"error": "Analysis failed or timed out", "details": str(e)}})

    crypto_is_scam = any(
        "honeypot" in str(c.get("analysis", "")).lower() for c in crypto_results
    )

    # ─── Decision Engine ───
    is_scam = (
        ai_analysis.get("is_scam", False)
        or keyword_confidence >= 0.45
        or crypto_is_scam
    )

    final_confidence = max(
        ai_analysis.get("confidence", 0),
        keyword_confidence,
        0.95 if crypto_is_scam else 0,
    )

    if is_scam:
        severity = "critical" if final_confidence >= 0.9 else "high" if final_confidence >= 0.7 else "medium"
        threat_in = ThreatCreate(
            type="smishing",
            source_number=sender,
            content=content,
            severity=severity,
            confidence_score=round(final_confidence, 3),
            metadata_json={
                "ai_reason": ai_analysis.get("reason", ""),
                "ai_category": ai_analysis.get("category", ""),
                "keyword_hits": keyword_score,
                "url_hits": url_score,
                "crypto_analysis": crypto_results,
            },
        )
        logger.warning("THREAT DETECTED: type=smishing severity=%s conf=%.3f sender=%s", severity, final_confidence, sender)
        return await create_threat(db=db, threat_in=threat_in, current_user=current_user)

    raise HTTPException(status_code=204, detail="No threat detected")


@router.post("/voice-intent")
async def detect_voice_intent(
    *,
    transcript: str,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Analyze live call transcript for scam intent using Groq."""
    if not client:
        return {"is_scam": False, "confidence": 0, "message": "AI engine offline"}

    logger.info("Voice intent scan from user=%d len=%d", current_user.id, len(transcript))

    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Analyze this live call transcript. Is the caller trying to "
                        "coerce the victim into sending money, revealing OTP, or "
                        "pretending to be an official? Return JSON: "
                        '{"is_scam": bool, "confidence": float, "intent": "description", '
                        '"urgency_level": "low|medium|high|critical"}'
                    ),
                },
                {"role": "user", "content": transcript},
            ],
            response_format={"type": "json_object"},
        )
        result = json.loads(completion.choices[0].message.content)
        logger.info("Voice analysis: scam=%s conf=%.2f", result.get("is_scam"), result.get("confidence", 0))
        return result
    except Exception as e:
        logger.error("Voice analysis failed: %s", e)
        return {"error": str(e), "is_scam": False}
