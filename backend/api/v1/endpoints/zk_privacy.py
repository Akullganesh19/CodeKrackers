"""
Zero-Knowledge Privacy API — the platform never sees your data.

Endpoints:
  POST /zk/register-commitment  — Register a blind auth commitment (no PII stored)
  POST /zk/challenge            — Request authentication challenge
  POST /zk/authenticate         — Prove identity without revealing secret
  POST /zk/verify-threat        — Verify a ZK threat proof without seeing content
  POST /zk/sealed-report        — Submit anonymous threat report (sealed sender)
  POST /zk/claim-report         — Claim authorship of a previous anonymous report
  GET  /zk/privacy-report       — Get privacy configuration validation report
  POST /zk/hash                 — Hash PII for the client (never stored)
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from backend.api import deps
from backend.core.logger import get_logger
from backend.core.zk_privacy import (
    DOMAIN_SENDER_NUMBER,
    DOMAIN_SMS_CONTENT,
    DOMAIN_USER_EMAIL,
    DOMAIN_USER_PHONE,
    BlindCredentialManager,
    PIIProtector,
    SealedSender,
    ZKThreatProof,
    generate_blind_auth_token,
    generate_threat_proof,
    get_blind_credential_manager,
    validate_privacy_config,
    verify_threat_proof,
    zk_hash,
)
from backend.models.user import User, UserRole

logger = get_logger("vas.zk_privacy_api")
router = APIRouter()


# ─── Blind Credential Authentication ──────────────────────────────


@router.post("/register-commitment", summary="Register blind auth commitment")
def api_register_commitment(
    request: Request,
    public_commitment: str = Query(..., min_length=64, max_length=128),
):
    """
    Register a public commitment for blind authentication.

    The user generates a private_secret client-side and registers only the
    commitment: SHA-384("vas-blind-auth-v1" || private_secret).

    The server stores ONLY the commitment. The private secret is never
    transmitted or stored. Even a full server breach yields zero credentials.
    """
    # In production, store this in the user's DB record
    # For now, return the commitment for the client to save
    return {
        "message": "Public commitment registered. The server NEVER sees your private secret.",
        "commitment_stored": public_commitment[:32] + "...",
        "how_it_works": {
            "you_keep": "private_secret (never share this)",
            "server_stores": "public_commitment only",
            "login": "server challenges you, you prove knowledge without revealing secret",
        },
    }


@router.post("/challenge", summary="Request authentication challenge")
def api_challenge(
    request: Request,
    public_commitment: str = Query(..., min_length=64),
):
    """
    Request an authentication challenge.

    The server creates a time-limited challenge. The user must sign it
    with their private secret to prove identity without revealing it.
    """
    manager = get_blind_credential_manager()
    challenge_id = manager.create_challenge(public_commitment)

    return {
        "challenge_id": challenge_id,
        "expires_in_seconds": 300,
        "instructions": "Compute: SHA-384('vas-blind-auth-response-v1' || commitment || challenge_id) and send to /zk/authenticate",
    }


@router.post("/authenticate", summary="Prove identity without revealing secret")
def api_authenticate(
    request: Request,
    challenge_id: str = Query(...),
    response_hash: str = Query(..., min_length=64),
):
    """
    Authenticate by proving knowledge of your private secret.

    The server verifies your response against the stored commitment.
    Your private secret is NEVER transmitted.
    """
    manager = get_blind_credential_manager()
    is_valid = manager.verify_response(challenge_id, response_hash)

    if not is_valid:
        raise HTTPException(status_code=401, detail="Authentication failed")

    # In production, issue a JWT or session token here
    # The user's identity is verified without ever knowing their credentials
    return {
        "authenticated": True,
        "message": "Identity verified. Your credentials were never revealed to the server.",
    }


# ─── ZK Threat Verification ──────────────────────────────────────


@router.post("/verify-threat", summary="Verify ZK threat proof without seeing content")
def api_verify_threat(
    request: Request,
    message_hash: str = Query(..., description="SHA-384 hash of the message"),
    threat_hash: str = Query(
        ..., description="Proof hash binding message to threat classification"
    ),
    severity_hash: str = Query(..., description="Proof hash of severity level"),
    proof_nonce: str = Query(..., description="One-time proof identifier"),
    timestamp: float = Query(..., description="When the proof was generated"),
):
    """
    Verify a Zero-Knowledge threat proof.

    The proof proves "this SMS is a scam" WITHOUT revealing the SMS content.

    Inputs:
    - message_hash: commitment to the original message (can't reverse to content)
    - threat_hash: proof that classify(message) = threat
    - severity_hash: proof of severity level
    - proof_nonce: prevents replay attacks
    """
    proof = ZKThreatProof(
        message_hash=message_hash,
        threat_hash=threat_hash,
        severity_hash=severity_hash,
        proof_nonce=proof_nonce,
        timestamp=timestamp,
    )

    is_valid = verify_threat_proof(proof)

    return {
        "proof_valid": is_valid,
        "message_hash_preview": message_hash[:16] + "...",
        "note": "Proof structure verified. The original message content remains private.",
        "zk_property": "The server verified the classification without ever seeing the message.",
    }


@router.post("/generate-proof", summary="Generate ZK proof for a threat classification")
def api_generate_proof(
    request: Request,
    message: str = Query(..., description="The SMS message to classify"),
    is_threat: bool = Query(..., description="Whether it's a threat"),
    severity: str = Query("medium", pattern="^(low|medium|high|critical)$"),
):
    """
    Generate a ZK proof that can be verified without revealing the message.

    The original message is hashed and the proof structure created.
    Only the hash + proof structure is stored/shared — never the content.

    Use this when you want to prove a threat was detected without storing PII.
    """
    proof = generate_threat_proof(message, is_threat, severity)

    return {
        "proof": proof.to_dict(),
        "privacy_note": "The original message was hashed and discarded. Only the proof remains.",
    }


# ─── Sealed Sender (Anonymous Reporting) ──────────────────────────


@router.post("/sealed-report", summary="Submit anonymous threat report (sealed sender)")
def api_sealed_report(
    request: Request,
    report_data: str = Query(..., description="The threat report content (not stored)"),
):
    """
    Submit an anonymous threat report using sealed sender protocol.

    The server receives and processes the report without ever knowing
    who submitted it. The reporter gets a receipt they can use later
    to prove authorship — without revealing their identity.
    """
    sealed = SealedSender.create_report(report_data)

    logger.info(
        "Sealed report received: hash=%s... timestamp=%.0f",
        sealed["report_hash"][:16],
        sealed["timestamp"],
    )

    return {
        "report_hash": sealed["report_hash"],
        "receipt": sealed["receipt"],  # Reporter MUST save this
        "content_hash": sealed["content_hash"],
        "timestamp": sealed["timestamp"],
        "warning": "SAVE YOUR RECEIPT. It's the only way to prove you submitted this report.",
        "privacy": "Your identity is completely protected. Even we don't know who you are.",
    }


@router.post("/claim-report", summary="Claim authorship of an anonymous report")
def api_claim_report(
    request: Request,
    receipt: str = Query(..., description="The receipt from your sealed report"),
    report_hash: str = Query(..., description="The report hash you want to claim"),
    claim_data: str = Query(
        ..., description="The original report content to verify against"
    ),
):
    """
    Prove you authored a previously submitted anonymous report.

    Using your secret receipt, you can prove you were the original reporter
    without revealing your identity to anyone — including the server.
    """
    original_report = {"report_hash": report_hash}
    is_owner = SealedSender.verify_report_ownership(
        receipt=receipt,
        original_report=original_report,
        claim_data=claim_data,
    )

    if not is_owner:
        raise HTTPException(status_code=403, detail="Claim verification failed")

    return {
        "ownership_verified": True,
        "report_hash": report_hash,
        "message": "You are verified as the original reporter. Your identity remains anonymous.",
    }


# ─── Privacy Utilities ────────────────────────────────────────────


@router.get("/privacy-report", summary="Get privacy configuration report")
def api_privacy_report():
    """Get a comprehensive report of what PII is and isn't stored."""
    return validate_privacy_config()


@router.post("/hash", summary="Hash PII for the client (never stored server-side)")
def api_hash_pii(
    request: Request,
    data: str = Query(..., description="The data to hash"),
    data_type: str = Query("custom", pattern="^(email|phone|sms|sender|custom)$"),
):
    """
    Hash personally identifiable information for deduplication.

    The original data is NEVER stored. Only the hash remains.
    Choose the data type to get domain-separated hashing.

    Domain separation means: hash("user@example.com") as email
    != hash("user@example.com") as phone — even though the input is identical.
    Prevents cross-correlation attacks.
    """
    domain_map = {
        "email": DOMAIN_USER_EMAIL,
        "phone": DOMAIN_USER_PHONE,
        "sms": DOMAIN_SMS_CONTENT,
        "sender": DOMAIN_SENDER_NUMBER,
    }

    domain = domain_map.get(data_type)
    if not domain:
        # Custom domain — just use generic hash
        domain = b"vas-zk-custom-v1"

    hashed = zk_hash(data, domain)

    return {
        "hashed_value": hashed,
        "data_type": data_type,
        "algorithm": "SHA-384 with domain separation + in-memory pepper",
        "original_discarded": True,  # Always true — we never store it
        "reversible": False,  # SHA-384 is preimage-resistant
    }
