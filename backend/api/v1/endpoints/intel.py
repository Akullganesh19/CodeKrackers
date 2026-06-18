"""
Intelligence gathering endpoints — consent management, phone lookup, device registration.
All endpoints require explicit user permission before collecting any data.
"""
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend.api import deps
from backend.models.intel import DeviceInfo, PhoneLookup, UserConsent
from backend.models.user import User
from backend.services.phone_intel import check_user_consent, lookup_phone_number

logger = logging.getLogger("vas.intel")
router = APIRouter()


# ─── CONSENT MANAGEMENT ───

@router.get("/consent")
def get_consent_status(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get current user's consent status."""
    consent = (
        db.query(UserConsent)
        .filter(UserConsent.user_id == current_user.id, UserConsent.is_revoked == False)
        .order_by(UserConsent.consent_given_at.desc())
        .first()
    )
    if not consent:
        return {
            "has_consent": False,
            "message": "No consent given yet. Grant permissions to enable intelligence gathering.",
            "permissions": {
                "phone_lookup": False,
                "device_info": False,
                "location": False,
                "sms_scan": False,
                "call_recording": False,
            },
        }

    return {
        "has_consent": True,
        "consent_id": consent.id,
        "given_at": consent.consent_given_at.isoformat() if consent.consent_given_at else None,
        "permissions": {
            "phone_lookup": consent.consent_phone_lookup,
            "device_info": consent.consent_device_info,
            "location": consent.consent_location,
            "sms_scan": consent.consent_sms_scan,
            "call_recording": consent.consent_call_recording,
        },
    }


@router.post("/consent")
def grant_consent(
    body: dict,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Grant data collection consent.
    Body: { "phone_lookup": true, "device_info": true, "location": false, ... }
    The user must explicitly opt-in to each type.
    """
    # Revoke any existing consent first
    existing = (
        db.query(UserConsent)
        .filter(UserConsent.user_id == current_user.id, UserConsent.is_revoked == False)
        .all()
    )
    for old in existing:
        old.is_revoked = True
        old.revoked_at = datetime.now(timezone.utc)

    # Create new consent record
    consent = UserConsent(
        user_id=current_user.id,
        consent_phone_lookup=body.get("phone_lookup", False),
        consent_device_info=body.get("device_info", False),
        consent_location=body.get("location", False),
        consent_sms_scan=body.get("sms_scan", False),
        consent_call_recording=body.get("call_recording", False),
        consent_ip=request.client.host if request.client else None,
        consent_user_agent=request.headers.get("user-agent", "")[:512],
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)

    logger.info(
        "CONSENT_GRANTED user=%d phone=%s device=%s location=%s sms=%s call=%s ip=%s",
        current_user.id,
        consent.consent_phone_lookup,
        consent.consent_device_info,
        consent.consent_location,
        consent.consent_sms_scan,
        consent.consent_call_recording,
        consent.consent_ip,
    )

    return {
        "message": "Consent recorded successfully",
        "consent_id": consent.id,
        "permissions": {
            "phone_lookup": consent.consent_phone_lookup,
            "device_info": consent.consent_device_info,
            "location": consent.consent_location,
            "sms_scan": consent.consent_sms_scan,
            "call_recording": consent.consent_call_recording,
        },
    }


@router.delete("/consent")
def revoke_consent(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Revoke all data collection consent immediately."""
    consents = (
        db.query(UserConsent)
        .filter(UserConsent.user_id == current_user.id, UserConsent.is_revoked == False)
        .all()
    )
    for c in consents:
        c.is_revoked = True
        c.revoked_at = datetime.now(timezone.utc)
    db.commit()

    logger.info("CONSENT_REVOKED user=%d count=%d", current_user.id, len(consents))
    return {"message": "All data collection consent has been revoked", "revoked_count": len(consents)}


# ─── PHONE NUMBER INTELLIGENCE ───

@router.post("/phone/lookup")
def phone_lookup(
    body: dict,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Look up intelligence on a phone number.
    Requires: consent_phone_lookup = True
    Returns carrier info, VoIP detection, risk score.
    """
    phone = body.get("phone_number", "").strip()
    threat_id = body.get("threat_id")

    if not phone:
        raise HTTPException(status_code=422, detail="phone_number is required")

    result = lookup_phone_number(
        db=db,
        phone_number=phone,
        user_id=current_user.id,
        threat_id=threat_id,
    )

    if result.get("error") == "consent_required":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result["message"],
        )

    return result


@router.get("/phone/history")
def phone_lookup_history(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get all phone lookups performed by the user."""
    lookups = (
        db.query(PhoneLookup)
        .filter(PhoneLookup.looked_up_by == current_user.id)
        .order_by(PhoneLookup.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "phone_number": l.phone_number,
            "carrier": l.carrier_name,
            "type": l.carrier_type,
            "is_voip": l.is_voip,
            "risk_score": l.risk_score,
            "looked_up_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in lookups
    ]


# ─── DEVICE FINGERPRINT COLLECTION ───

@router.post("/device/register")
def register_device(
    body: dict,
    request: Request,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Register device information for forensic purposes.
    Requires: consent_device_info = True
    Called by mobile app or web dashboard on login.
    """
    if not check_user_consent(db, current_user.id, "consent_device_info"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device data collection requires explicit consent. Please grant permission first.",
        )

    device = DeviceInfo(
        user_id=current_user.id,
        # Device
        device_model=body.get("device_model"),
        device_brand=body.get("device_brand"),
        os_name=body.get("os_name"),
        os_version=body.get("os_version"),
        app_version=body.get("app_version"),
        # Network
        ip_address=request.client.host if request.client else None,
        network_type=body.get("network_type"),
        carrier_name=body.get("carrier_name"),
        sim_operator=body.get("sim_operator"),
        sim_country=body.get("sim_country"),
        # Location (only if consent)
        latitude=body.get("latitude") if check_user_consent(db, current_user.id, "consent_location") else None,
        longitude=body.get("longitude") if check_user_consent(db, current_user.id, "consent_location") else None,
        city=body.get("city"),
        state=body.get("state"),
        # Browser
        browser_name=body.get("browser_name"),
        browser_version=body.get("browser_version"),
        screen_resolution=body.get("screen_resolution"),
        timezone=body.get("timezone"),
        language=body.get("language"),
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    logger.info(
        "DEVICE_REGISTERED user=%d model=%s os=%s ip=%s",
        current_user.id,
        device.device_model,
        device.os_name,
        device.ip_address,
    )

    return {
        "message": "Device registered successfully",
        "device_id": device.id,
        "ip": device.ip_address,
    }


@router.get("/device/list")
def list_user_devices(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """List all registered devices for the current user."""
    devices = (
        db.query(DeviceInfo)
        .filter(DeviceInfo.user_id == current_user.id)
        .order_by(DeviceInfo.created_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": d.id,
            "device": f"{d.device_brand or ''} {d.device_model or ''}".strip() or "Unknown",
            "os": f"{d.os_name or ''} {d.os_version or ''}".strip(),
            "ip": d.ip_address,
            "carrier": d.carrier_name,
            "network": d.network_type,
            "location": f"{d.city or ''}, {d.state or ''}".strip(", ") if d.city or d.state else None,
            "registered_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in devices
    ]
