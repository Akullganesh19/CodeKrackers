"""
Nitro Enclave API Endpoints — FastAPI routes that proxy detection to the enclave.

These endpoints expose the hardware-isolated ML inference to the rest of the system.
In production, requests are sent over vsock with AES-256-GCM encryption.
In mock mode, they call the enclave functions directly for development/testing.

Architecture:
  User → FastAPI Host → vsock (encrypted) → Nitro Enclave → ML Inference
                    ← vsock (encrypted) ←
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.enclave.enclave_client import (
    MOCK_MODE,
    check_enclave_health,
    detect_sms_in_enclave,
    detect_voice_in_enclave,
    get_enclave_attestation,
    set_shared_key,
)

logger = logging.getLogger("vas.enclave_api")

router = APIRouter()


# ─── Request Models ────────────────────────────────────────────────


class SMSDetectionRequest(BaseModel):
    sms_text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The SMS message text to classify inside the enclave",
    )


class VoiceDetectionRequest(BaseModel):
    transcript: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Voice call transcript to analyze for vishing patterns",
    )


class AttestationRequest(BaseModel):
    user_data: str = Field(
        "",
        max_length=4096,
        description="Optional data to include in the attestation document",
    )


class KeyExchangeRequest(BaseModel):
    shared_key_hex: str = Field(
        ...,
        min_length=64,
        max_length=64,
        description="64-char hex string representing 32-byte AES-256-GCM shared key",
    )


# ─── Endpoints ─────────────────────────────────────────────────────


@router.post(
    "/detect/sms",
    summary="Classify SMS in hardware-isolated enclave",
    description=(
        "Sends SMS text to the Nitro Enclave for ML-based smishing detection. "
        "The enclave decrypts, runs inference, and returns results — all in "
        "hardware-isolated memory that the host OS cannot access."
    ),
)
async def detect_sms_endpoint(request: SMSDetectionRequest) -> Dict[str, Any]:
    """
    Classify an SMS message inside the hardware enclave.

    The SMS text is encrypted with AES-256-GCM, sent over vsock to the
    Nitro Enclave, classified inside isolated memory, and the result
    is encrypted and returned.
    """
    try:
        result = detect_sms_in_enclave(request.sms_text)
        return result
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Enclave unavailable: {e}",
        )
    except Exception as e:
        logger.exception("Enclave SMS detection failed")
        raise HTTPException(
            status_code=500,
            detail=f"Enclave inference error: {e}",
        )


@router.post(
    "/detect/voice",
    summary="Classify voice transcript in hardware-isolated enclave",
    description=(
        "Sends a voice call transcript to the Nitro Enclave for vishing detection. "
        "The enclave analyzes coercion patterns and scam keywords in isolation."
    ),
)
async def detect_voice_endpoint(request: VoiceDetectionRequest) -> Dict[str, Any]:
    """
    Classify a voice call transcript inside the hardware enclave.

    Detects vishing (voice phishing) patterns including coercion,
    impersonation, and urgent-action requests.
    """
    try:
        result = detect_voice_in_enclave(request.transcript)
        return result
    except (ConnectionError, TimeoutError) as e:
        raise HTTPException(
            status_code=503,
            detail=f"Enclave unavailable: {e}",
        )
    except Exception as e:
        logger.exception("Enclave voice detection failed")
        raise HTTPException(
            status_code=500,
            detail=f"Enclave inference error: {e}",
        )


@router.get(
    "/attestation",
    summary="Get Nitro Enclave attestation document",
    description=(
        "Retrieves the enclave attestation document proving it is running "
        "in genuine AWS Nitro hardware. In production, clients verify this "
        "document via AWS KMS to ensure the enclave hasn't been tampered with."
    ),
)
async def attestation_endpoint(
    user_data: str = "",
) -> Dict[str, Any]:
    """
    Get cryptographic proof that the enclave is genuine hardware.

    Returns PCR values (Platform Configuration Registers) that represent
    the enclave's identity — image hash, kernel hash, application hash.
    """
    try:
        result = get_enclave_attestation(user_data)
        return result
    except Exception as e:
        logger.exception("Enclave attestation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Attestation error: {e}",
        )


@router.get(
    "/health",
    summary="Check enclave connectivity and status",
    description=(
        "Health check that verifies the enclave is reachable and functional. "
        "In mock mode, confirms the mock enclave is operational. "
        "In production mode, tests vsock connectivity to CID=16."
    ),
)
async def enclave_health_endpoint() -> Dict[str, Any]:
    """Check if the Nitro Enclave is reachable and responding."""
    return check_enclave_health()


@router.post(
    "/key-exchange",
    summary="Set shared AES-256-GCM key after attestation",
    description=(
        "After the attestation handshake, the host and enclave agree on a "
        "shared AES-256-GCM key. This endpoint allows the admin to set that "
        "key on the host side for subsequent encrypted communication."
    ),
)
async def key_exchange_endpoint(request: KeyExchangeRequest) -> Dict[str, Any]:
    """
    Set the shared AES-256-GCM encryption key for enclave communication.

    This key should be obtained via the Nitro Attestation process:
    1. Enclave generates a key during boot
    2. Host calls GET /attestation to get the enclave's attestation
    3. Host verifies attestation via AWS KMS
    4. Enclave securely transmits the key to the host
    5. Host calls this endpoint to register the key
    """
    if MOCK_MODE:
        return {
            "status": "skipped",
            "note": "Mock mode — key exchange not needed",
            "mode": "mock",
        }

    try:
        key_bytes = bytes.fromhex(request.shared_key_hex)
        set_shared_key(key_bytes)
        return {
            "status": "success",
            "note": "Shared AES-256-GCM key registered",
            "mode": "production",
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid key format: {e}",
        )
    except Exception as e:
        logger.exception("Key exchange failed")
        raise HTTPException(
            status_code=500,
            detail=f"Key exchange error: {e}",
        )


@router.get(
    "/status",
    summary="Get enclave security configuration details",
    description=(
        "Returns detailed information about the enclave configuration including "
        "encryption status, attestation support, and hardware isolation level."
    ),
)
async def enclave_status_endpoint() -> Dict[str, Any]:
    """Get comprehensive enclave security configuration status."""
    health = check_enclave_health()

    return {
        "enclave_type": (
            "AWS Nitro Enclaves" if not MOCK_MODE else "Mock Enclave (Demo)"
        ),
        "encryption": "AES-256-GCM",
        "key_size": 256,
        "communication": (
            "vsock (CID=16, port=5000)" if not MOCK_MODE else "in-process (mock)"
        ),
        "attestation": (
            "AWS Nitro Attestation" if not MOCK_MODE else "Simulated (PCR mock)"
        ),
        "model_inference": (
            "Hardware-isolated memory"
            if not MOCK_MODE
            else "Fallback keyword classifier"
        ),
        "reachable": health.get("enclave_reachable", False),
        "mode": MOCK_MODE and "mock" or "production",
    }
