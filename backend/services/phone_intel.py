"""
Phone number intelligence service — 100% open-source, no paid APIs.
Uses Google's libphonenumber (phonenumbers) for offline analysis.
"""
import logging
from typing import Any, Dict, Optional

import phonenumbers
from phonenumbers import carrier, geocoder, timezone as pn_tz, number_type
from phonenumbers.phonenumberutil import PhoneNumberType
from sqlalchemy.orm import Session

from backend.models import PhoneLookup, UserConsent

logger = logging.getLogger("vas.phone_intel")

# ─── Number type to human-readable + risk mapping ───
NUMBER_TYPE_MAP = {
    PhoneNumberType.MOBILE: ("mobile", 0.1),
    PhoneNumberType.FIXED_LINE: ("landline", 0.05),
    PhoneNumberType.FIXED_LINE_OR_MOBILE: ("fixed_or_mobile", 0.1),
    PhoneNumberType.TOLL_FREE: ("toll_free", 0.3),
    PhoneNumberType.PREMIUM_RATE: ("premium_rate", 0.6),
    PhoneNumberType.SHARED_COST: ("shared_cost", 0.3),
    PhoneNumberType.VOIP: ("voip", 0.8),          # VoIP = HIGH scam signal
    PhoneNumberType.PERSONAL_NUMBER: ("personal", 0.2),
    PhoneNumberType.PAGER: ("pager", 0.4),
    PhoneNumberType.UAN: ("uan", 0.2),
    PhoneNumberType.UNKNOWN: ("unknown", 0.5),
}

# ─── Indian telecom circle mapping ───
INDIAN_CIRCLES = {
    "11": "Delhi", "22": "Mumbai", "33": "Kolkata", "44": "Chennai",
    "40": "Hyderabad", "80": "Bangalore", "79": "Ahmedabad", "20": "Pune",
    "141": "Jaipur", "522": "Lucknow", "512": "Kanpur", "120": "Noida",
    "124": "Gurugram",
}

# ─── Known scam area codes (international) ───
HIGH_RISK_COUNTRIES = {
    "NG": ("Nigeria", 0.7),   # 419 scams
    "GH": ("Ghana", 0.5),
    "CI": ("Ivory Coast", 0.5),
    "PH": ("Philippines", 0.3),
    "RO": ("Romania", 0.4),
}


def check_user_consent(db: Session, user_id: int, consent_type: str) -> bool:
    """Verify that the user has given specific consent."""
    consent = (
        db.query(UserConsent)
        .filter(UserConsent.user_id == user_id, UserConsent.is_revoked is False)
        .order_by(UserConsent.consent_given_at.desc())
        .first()
    )
    if not consent:
        return False
    return getattr(consent, consent_type, False)


def analyze_phone_number(phone_raw: str) -> Dict[str, Any]:
    """
    Full offline phone number analysis using libphonenumber.
    No external API calls, no subscriptions needed.
    """
    result = {
        "phone_number": phone_raw,
        "is_valid": False,
        "country_code": None,
        "national_format": None,
        "international_format": None,
        "carrier": {"name": None, "type": None, "is_voip": False},
        "location": {"description": None, "timezones": []},
        "risk_assessment": {"score": "low", "base_risk": 0.0, "fraud_indicators": []},
    }

    try:
        # Parse — default to India if no country code
        parsed = phonenumbers.parse(phone_raw, "IN")

        # Validity
        result["is_valid"] = phonenumbers.is_valid_number(parsed)
        result["is_possible"] = phonenumbers.is_possible_number(parsed)

        if not result["is_valid"] and not result["is_possible"]:
            result["risk_assessment"]["fraud_indicators"].append("Invalid phone number format")
            result["risk_assessment"]["score"] = "high"
            result["risk_assessment"]["base_risk"] = 0.7
            return result

        # Formatting
        result["country_code"] = phonenumbers.region_code_for_number(parsed)
        result["national_format"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        result["international_format"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        # Carrier
        carrier_name = carrier.name_for_number(parsed, "en")
        result["carrier"]["name"] = carrier_name or "Unknown"

        # Number type (mobile, landline, VoIP, etc.)
        num_type = number_type(parsed)
        type_info = NUMBER_TYPE_MAP.get(num_type, ("unknown", 0.5))
        result["carrier"]["type"] = type_info[0]
        result["carrier"]["is_voip"] = num_type == PhoneNumberType.VOIP
        base_risk = type_info[1]

        # Location / geocoding
        location_desc = geocoder.description_for_number(parsed, "en")
        result["location"]["description"] = location_desc or "Unknown"

        # Timezones
        tz_list = pn_tz.time_zones_for_number(parsed)
        result["location"]["timezones"] = list(tz_list) if tz_list else []

        # ─── Risk Assessment ───
        fraud_indicators = []

        # VoIP detection
        if result["carrier"]["is_voip"]:
            fraud_indicators.append("VoIP number - commonly used by scammers to hide identity")
            base_risk = max(base_risk, 0.8)

        # Premium rate
        if num_type == PhoneNumberType.PREMIUM_RATE:
            fraud_indicators.append("Premium rate number - potential revenue scam")
            base_risk = max(base_risk, 0.6)

        # International call to India
        country = result["country_code"]
        if country and country != "IN":
            fraud_indicators.append(f"International number from {country}")
            base_risk = max(base_risk, 0.3)

            # Known high-risk country
            if country in HIGH_RISK_COUNTRIES:
                country_name, country_risk = HIGH_RISK_COUNTRIES[country]
                fraud_indicators.append(f"High-risk origin country: {country_name}")
                base_risk = max(base_risk, country_risk)

        # Unknown carrier
        if not carrier_name:
            fraud_indicators.append("Carrier not identified - possible virtual/spoofed number")
            base_risk = max(base_risk, 0.4)

        # Determine score label
        if base_risk >= 0.7:
            score = "high"
        elif base_risk >= 0.4:
            score = "medium"
        else:
            score = "low"

        result["risk_assessment"] = {
            "score": score,
            "base_risk": round(base_risk, 3),
            "fraud_indicators": fraud_indicators,
        }

        return result

    except phonenumbers.NumberParseException as e:
        result["risk_assessment"]["fraud_indicators"].append(f"Cannot parse number: {str(e)}")
        result["risk_assessment"]["score"] = "high"
        result["risk_assessment"]["base_risk"] = 0.8
        return result


def lookup_phone_number(
    db: Session,
    phone_number: str,
    user_id: int,
    threat_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Full phone intelligence lookup with consent check and DB caching.
    REQUIRES: consent_phone_lookup = True
    """
    # Step 1: Check consent
    if not check_user_consent(db, user_id, "consent_phone_lookup"):
        logger.warning("PHONE_LOOKUP_DENIED user=%d - no consent", user_id)
        return {
            "error": "consent_required",
            "message": "Phone lookup requires explicit user consent. Please grant permission first.",
        }

    # Step 2: Check cache
    existing = (
        db.query(PhoneLookup)
        .filter(PhoneLookup.phone_number == phone_number)
        .order_by(PhoneLookup.created_at.desc())
        .first()
    )
    if existing:
        logger.info("PHONE_LOOKUP_CACHED phone=%s", phone_number)
        return _format_lookup(existing)

    # Step 3: Analyze using libphonenumber (offline, free)
    analysis = analyze_phone_number(phone_number)

    # Step 4: Store result
    lookup = PhoneLookup(
        phone_number=phone_number,
        looked_up_by=user_id,
        country_code=analysis["country_code"],
        national_format=analysis["national_format"],
        carrier_name=analysis["carrier"]["name"],
        carrier_type=analysis["carrier"]["type"],
        is_voip=analysis["carrier"]["is_voip"],
        risk_score=analysis["risk_assessment"]["score"],
        fraud_indicators=analysis["risk_assessment"]["fraud_indicators"],
        threat_id=threat_id,
    )
    db.add(lookup)
    db.commit()
    db.refresh(lookup)

    logger.info(
        "PHONE_LOOKUP phone=%s carrier=%s type=%s voip=%s risk=%s",
        phone_number,
        analysis["carrier"]["name"],
        analysis["carrier"]["type"],
        analysis["carrier"]["is_voip"],
        analysis["risk_assessment"]["score"],
    )
    return analysis


def _format_lookup(lookup: PhoneLookup) -> Dict[str, Any]:
    return {
        "phone_number": lookup.phone_number,
        "is_valid": True,
        "country_code": lookup.country_code,
        "national_format": lookup.national_format,
        "carrier": {
            "name": lookup.carrier_name,
            "type": lookup.carrier_type,
            "is_voip": lookup.is_voip,
        },
        "risk_assessment": {
            "score": lookup.risk_score,
            "fraud_indicators": lookup.fraud_indicators or [],
        },
        "cached": True,
    }
