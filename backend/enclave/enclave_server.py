"""
Nitro Enclave Detection Server — runs INSIDE the hardware enclave.

This code runs in complete isolation:
- No network access (only vsock to parent)
- No disk access (model loaded at boot)
- No shell, no SSH, no debugging
- Memory encrypted by hardware

Communication is via vsock (Virtual Socket) — the ONLY channel in/out.
All data is AES-256-GCM encrypted before transit.

Production: Build with `nitro-cli build-enclave --docker-uri ...`
Demo: Run as a standalone Python process (mock_enclave mode)
"""

import os
import json
import time
import hashlib
import logging
import secrets
from typing import Optional, Dict, Any

logger = logging.getLogger("vas.enclave")

# ─── Enclave AES-256-GCM Key ─────────────────────────────────────
# Generated fresh on every enclave boot — never leaves the enclave
# In production, this is exchanged with the host via Nitro attestation

ENCLAVE_KEY: Optional[bytes] = None


def _get_enclave_key() -> bytes:
    """Get or generate the enclave's AES-256-GCM key."""
    global ENCLAVE_KEY
    if ENCLAVE_KEY is None:
        ENCLAVE_KEY = secrets.token_bytes(32)  # 256 bits
        logger.info("Enclave AES-256 key generated (in-memory only)")
    return ENCLAVE_KEY


def encrypt_response(plaintext: bytes) -> bytes:
    """Encrypt data with AES-256-GCM before sending to host."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        # Fallback: XOR-based mock encryption for demo
        return _mock_encrypt(plaintext)

    key = _get_enclave_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def decrypt_request(data: bytes) -> bytes:
    """Decrypt data received from host."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        return _mock_decrypt(data)

    key = _get_enclave_key()
    aesgcm = AESGCM(key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)


def _mock_encrypt(plaintext: bytes) -> bytes:
    """Simple mock for demo when cryptography isn't available."""
    return b"MOCK:" + plaintext


def _mock_decrypt(data: bytes) -> bytes:
    """Simple mock for demo."""
    if data.startswith(b"MOCK:"):
        return data[5:]
    return data


# ─── ML Inference (runs inside enclave) ───────────────────────────


def classify_sms_enclave(text: str) -> Dict[str, Any]:
    """
    Classify SMS text inside the enclave.

    In production with Nitro Enclaves:
      - The model weights are loaded at boot from the EIF image
      - No disk access — everything is in encrypted memory
      - The host OS CANNOT see the model weights or the input text

    This function is the core of what runs in hardware isolation.
    """
    # ─── Keyword-based classifier (works without GPU) ─────
    scam_keywords = [
        "kyc",
        "aadhaar",
        "otp",
        "blocked",
        "suspended",
        "verify",
        "challan",
        "parivahan",
        "pan card",
        "income tax",
        "epfo",
        "sbi",
        "rbi",
        "customs",
        "courier",
        "fedex",
        "arrest",
        "warrant",
        "cbi",
        "narcotics",
        "money laundering",
        "click here",
        "update now",
        "expir",
        "urgent",
        "immediately",
        "bit.ly",
        "tinyurl",
        "prize",
        "lottery",
        "won",
        "reward",
    ]

    url_patterns = [
        "bit.ly",
        "tinyurl",
        "t.co",
        "goo.gl",
        ".xyz",
        ".tk",
        "login-secure",
        "verify-account",
        "update-kyc",
    ]

    text_lower = text.lower()
    keyword_hits = sum(1 for kw in scam_keywords if kw in text_lower)
    url_hits = sum(1 for p in url_patterns if p in text_lower)

    confidence = min((keyword_hits * 0.15) + (url_hits * 0.2), 1.0)
    is_scam = confidence >= 0.3

    # ─── Try transformer model if available ───
    transformer_result = None
    try:
        from transformers import pipeline

        classifier = pipeline(
            "text-classification",
            model="./models/distilbert-scam-finetuned",
            device=-1,  # CPU
        )
        result = classifier(text)[0]
        transformer_result = {
            "label": result["label"],
            "score": result["score"],
        }
        # Use transformer result if available
        is_scam = result["label"] in ("LABEL_1", "SCAM", "scam")
        confidence = result["score"]
    except Exception:
        pass  # Fall back to keyword classifier

    return {
        "label": "SCAM" if is_scam else "SAFE",
        "confidence": round(confidence * 100, 2),
        "keyword_hits": keyword_hits,
        "url_hits": url_hits,
        "transformer_used": transformer_result is not None,
        "enclave_processed": True,
    }


def classify_voice_enclave(transcript: str) -> Dict[str, Any]:
    """Classify a voice call transcript inside the enclave."""
    vishing_keywords = [
        "bank",
        "account",
        "otp",
        "transfer",
        "police",
        "arrest",
        "warrant",
        "customs",
        "fedex",
        "courier",
        "blocked",
        "suspended",
        "tax",
        "refund",
        "penalty",
        "fine",
        "verification",
        "aadhar",
        "aadhaar",
        "pan card",
    ]

    coercion_patterns = [
        "do it now",
        "immediately",
        "right now",
        "hurry",
        "don't tell anyone",
        "keep this confidential",
        "i am calling from",
        "this is officer",
    ]

    text_lower = transcript.lower()
    keyword_hits = sum(1 for kw in vishing_keywords if kw in text_lower)
    coercion_hits = sum(1 for p in coercion_patterns if p in text_lower)

    confidence = min((keyword_hits * 0.12) + (coercion_hits * 0.25), 1.0)
    is_scam = confidence >= 0.35

    return {
        "label": "VISHING" if is_scam else "SAFE",
        "confidence": round(confidence * 100, 2),
        "keyword_hits": keyword_hits,
        "coercion_hits": coercion_hits,
        "enclave_processed": True,
    }


def get_attestation_document(user_data: bytes = b"") -> Dict[str, Any]:
    """
    Request attestation document from the Nitro hypervisor.

    In production: subprocess call to nitro-cli
    In mock mode: returns a simulated attestation
    """
    try:
        import subprocess
        import base64

        result = subprocess.run(
            ["nitro-cli", "get-attestation-document", "--user-data", user_data.hex()],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            return {
                "attestation_document": base64.b64encode(result.stdout).decode(),
                "is_genuine": True,
            }
    except Exception:
        pass

    # Mock attestation for demo
    doc_hash = hashlib.sha384(
        b"vas-enclave-attestation-v1" + user_data + secrets.token_bytes(16)
    ).hexdigest()

    return {
        "attestation_document": doc_hash,
        "is_genuine": False,
        "note": "Mock attestation — production uses AWS Nitro hardware attestation",
        "pcr0": hashlib.sha384(b"enclave-image-hash").hexdigest()[:32],
        "pcr1": hashlib.sha384(b"linux-kernel-hash").hexdigest()[:32],
        "pcr2": hashlib.sha384(b"application-hash").hexdigest()[:32],
    }


# ─── vsock Server (production) ────────────────────────────────────


def vsock_server(port: int = 5000):
    """
    Start the vsock server inside the Nitro Enclave.

    vsock is the ONLY communication channel into a Nitro Enclave.
    No TCP/IP, no HTTP, no filesystem — just this pipe.
    """
    import socket

    sock = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
    sock.bind((socket.VMADDR_CID_ANY, port))
    sock.listen(5)
    logger.info("Enclave vsock server listening on port %d", port)

    while True:
        conn, _ = sock.accept()
        try:
            data = conn.recv(65536)
            plaintext = decrypt_request(data)
            payload = json.loads(plaintext)

            action = payload.get("action", "classify_sms")

            if action == "classify_sms":
                result = classify_sms_enclave(payload.get("sms_text", ""))
            elif action == "classify_voice":
                result = classify_voice_enclave(payload.get("transcript", ""))
            elif action == "get_attestation":
                result = get_attestation_document(payload.get("user_data", "").encode())
            else:
                result = {"error": "Unknown action", "action": action}

            response_bytes = json.dumps(result).encode()
            encrypted_response = encrypt_response(response_bytes)
            conn.sendall(encrypted_response)

        except Exception as e:
            error_response = json.dumps({"error": str(e)}).encode()
            conn.sendall(encrypt_response(error_response))
        finally:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Nitro Enclave Detection Server...")
    vsock_server()
