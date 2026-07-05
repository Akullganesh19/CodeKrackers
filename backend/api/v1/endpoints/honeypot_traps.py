"""
Honeypot endpoints - decoy APIs that look real to trap attackers.
"""

import logging
import secrets
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse

from backend.db.session import SessionLocal
from backend.models.honeypot import HoneypotAccess

logger = logging.getLogger("vas.honeypot")
router = APIRouter()


def log_honeypot_to_db(
    endpoint: str,
    ip_address: str,
    user_agent: str,
    method: str,
    query_params: Optional[dict] = None,
    headers: Optional[dict] = None,
    body_preview: Optional[str] = None,
    is_authenticated: bool = False,
    risk_score: int = 0,
    threat_indicators: Optional[list] = None,
):
    """Write honeypot access record to database in a separate session."""
    try:
        db = SessionLocal()
        access = HoneypotAccess(
            timestamp=datetime.now(timezone.utc),
            ip_address=ip_address,
            user_agent=user_agent[:512] if user_agent else None,
            endpoint=endpoint,
            method=method,
            query_params=query_params,
            headers=headers,
            body_preview=body_preview[:512] if body_preview else None,
            is_authenticated=is_authenticated,
            risk_score=risk_score,
            threat_indicators=threat_indicators or [],
        )
        db.add(access)
        db.commit()
        db.close()
    except Exception as e:
        logger.error("Failed to log honeypot access to DB: %s", e)


# ─── Admin User Export Probe ───
@router.get("/admin/export-users")
def honeypot_export_users(
    request: Request, format: str = Query("csv", pattern="^(csv|json|xlsx)$")
):
    """Fake admin endpoint: appears to export all user data."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    is_authenticated = bool(request.headers.get("authorization", ""))
    risk_score = 50 + (20 if not is_authenticated else 0)

    log_honeypot_to_db(
        endpoint="/api/v1/admin/export-users",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        query_params=dict(request.query_params),
        headers={k: v for k, v in request.headers.items()},
        is_authenticated=is_authenticated,
        risk_score=risk_score,
        threat_indicators=["admin_probe"],
    )

    logger.warning(
        "HONEYPOT TRIGGERED ip=%s endpoint=/api/v1/admin/export-users risk=%d",
        client_ip,
        risk_score,
    )

    return JSONResponse(
        content={
            "detail": "Access denied: Insufficient privileges",
            "required_role": "SUPER_ADMIN",
            "honeypot_triggered": True,
        },
        status_code=403,
    )


# ─── Internal Models/Schema Disclosure ───
@router.get("/internal/models")
def honeypot_internal_models(request: Request):
    """Fake internal API exposing ORM models/schema."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/internal/models",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=60,
        threat_indicators=["reconnaissance", "schema_probe"],
    )

    return JSONResponse(
        content={
            "error": "Internal API endpoint not accessible",
            "honeypot_triggered": True,
        },
        status_code=403,
    )


# ─── Database Config Leak ───
@router.get("/config/database")
def honeypot_db_config(request: Request):
    """Fake endpoint that leaks database configuration."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/config/database",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=70,
        threat_indicators=["config_leak"],
    )

    return JSONResponse(
        content={"error": "Access denied", "honeypot_triggered": True}, status_code=403
    )


# ─── Debug Status Probe ───
@router.get("/debug/status")
def honeypot_debug_status(request: Request):
    """Fake debug endpoint exposing system status."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/debug/status",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=40,
        threat_indicators=["reconnaissance"],
    )

    return JSONResponse(
        content={"error": "Debug mode disabled", "honeypot_triggered": True},
        status_code=403,
    )


# ─── Backup Files Access ───
@router.get("/backup/threats.sql")
def honeypot_backup_download(request: Request):
    """Fake backup file download endpoint."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/backup/threats.sql",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=65,
        threat_indicators=["backup_access"],
    )

    return JSONResponse(
        content={
            "error": "Backup files not accessible via HTTP",
            "honeypot_triggered": True,
        },
        status_code=403,
    )


# ─── Secrets/API Keys Disclosure ───
@router.get("/secrets/api-keys")
def honeypot_secrets(request: Request):
    """Fake endpoint listing API keys/secrets - high-value target."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/secrets/api-keys",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=90,
        threat_indicators=["secret_leak"],
    )

    secrets.token_urlsafe(32)
    return JSONResponse(
        content={
            "error": "Unauthorized",
            "honeypot_triggered": True,
            "alert": "Logged and analyzed",
        },
        status_code=403,
    )


# ─── GraphQL Probe ───
@router.get("/graphql")
def honeypot_graphql_endpoint(request: Request):
    """Fake GraphQL endpoint - probes common even if not used."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/graphql",
        ip_address=client_ip,
        user_agent=user_agent,
        method="GET",
        headers={k: v for k, v in request.headers.items()},
        risk_score=30,
        threat_indicators=["graphql_probe"],
    )

    return JSONResponse(
        content={"error": "GraphQL not enabled", "honeypot_triggered": True},
        status_code=404,
    )


# ─── Admin Login Probe ───
@router.post("/admin/login")
def honeypot_admin_login(request: Request):
    """Fake admin login endpoint."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    log_honeypot_to_db(
        endpoint="/api/admin/login",
        ip_address=client_ip,
        user_agent=user_agent,
        method="POST",
        headers={k: v for k, v in request.headers.items()},
        risk_score=45,
        threat_indicators=["admin_login_attempt"],
    )

    return JSONResponse(
        content={
            "error": "Invalid endpoint",
            "hint": "Use /api/v1/login/access-token",
            "honeypot_triggered": True,
        },
        status_code=404,
    )


# ─── SQL Injection Probe ───
@router.get("/products")
def honeypot_sqli_probe(request: Request, id: str = "1"):
    """
    Decoy endpoint monitoring for SQL injection attempts.
    GET /api/products?id=1' UNION SELECT --
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    sqli_patterns = [
        "union",
        "select",
        "sleep(",
        "information_schema",
        "drop table",
        "' or '1'='1",
    ]
    id_lower = id.lower()
    detected = [p for p in sqli_patterns if p in id_lower]

    if detected:
        log_honeypot_to_db(
            endpoint="/api/products",
            ip_address=client_ip,
            user_agent=user_agent,
            method="GET",
            query_params=dict(request.query_params),
            headers={k: v for k, v in request.headers.items()},
            risk_score=80,
            threat_indicators=["sqli_probe"] + detected,
        )

        logger.error(
            "SQLi PROBE DETECTED ip=%s id=%s patterns=%s",
            client_ip,
            id,
            ",".join(detected),
        )

        return JSONResponse(
            content={
                "error": "Malicious request detected",
                "honeypot_triggered": True,
                "detected_patterns": detected,
            },
            status_code=403,
        )

    return JSONResponse({"detail": "Not found"}, status_code=404)


# ─── Path Traversal Probe ───
@router.get("/files")
def honeypot_path_traversal(request: Request, path: str = "report.pdf"):
    """
    Decoy file download endpoint - probes for path traversal.
    GET /api/files?path=../../../../etc/passwd
    """
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")

    dangerous_patterns = [
        "../",
        "..\\",
        "%2e%2e",
        "/etc/passwd",
        "/etc/shadow",
        "boot.ini",
    ]
    path_lower = path.lower()
    detected = [p for p in dangerous_patterns if p in path_lower]

    if detected:
        log_honeypot_to_db(
            endpoint="/api/files",
            ip_address=client_ip,
            user_agent=user_agent,
            method="GET",
            query_params=dict(request.query_params),
            headers={k: v for k, v in request.headers.items()},
            risk_score=75,
            threat_indicators=["path_traversal"] + detected,
        )

        return JSONResponse(
            content={
                "error": "Path traversal attack detected",
                "honeypot_triggered": True,
            },
            status_code=403,
        )

    return JSONResponse({"detail": "File not found"}, status_code=404)


# ─── SSRF Probe ───
@router.get("/fetch-url")
def honeypot_ssrf(request: Request, url: str = None):
    """
    Decoy endpoint that fetches remote URLs - probes for SSRF.
    GET /api/fetch-url?url=http://169.254.169.254/latest/meta-data/
    """
    if url:
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")

        ssrf_targets = [
            "127.0.0.1",
            "localhost",
            "169.254.169.254",
            "metadata.google.internal",
            "10.",
            "192.168.",
        ]
        url_lower = url.lower()
        detected = [t for t in ssrf_targets if t in url_lower]

        if detected:
            log_honeypot_to_db(
                endpoint="/api/fetch-url",
                ip_address=client_ip,
                user_agent=user_agent,
                method="GET",
                query_params=dict(request.query_params),
                headers={k: v for k, v in request.headers.items()},
                risk_score=85,
                threat_indicators=["ssrf_attempt"] + detected,
            )

            return JSONResponse(
                content={
                    "error": "SSRF attack detected",
                    "blocked_url": detected[0],
                    "honeypot_triggered": True,
                },
                status_code=403,
            )

    return JSONResponse({"error": "URL parameter required"}, status_code=400)
