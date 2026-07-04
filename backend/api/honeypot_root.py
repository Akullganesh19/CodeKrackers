"""
Root-level honeypot endpoints — mounted at exactly the paths attackers expect.

These are mounted at the root level (not under /api/v1) to catch attackers who
probe for:
  - /admin/export-users
  - /internal/models
  - /config/database
  - /.env
  - /backup.sql

These endpoints are never used by the real application. Any access is malicious.
"""
import time
from backend.core.logger import get_logger
import logging
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse

logger = get_logger("vas.honeypot_root")
router = APIRouter()


def _log_probe(request: Request, endpoint: str, risk_score: int = 50):
    """Log a honeypot probe with attacker details."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[:120]
    auth = request.headers.get("authorization", "")[:40]

    logger.warning(
        "HONEYPOT ROOT PROBE ip=%s endpoint=%s ua=%s auth=%s risk=%d",
        client_ip, endpoint, user_agent, auth or "none", risk_score,
    )

    # In production, also:
    # - GeoIP lookup on the IP
    # - Check IP against threat intel feeds
    # - Send alert to security team
    # - Auto-block at firewall if risk > 80


@router.get("/admin/export-users")
async def honeypot_admin_export_users(
    request: Request,
    format: str = Query("csv"),
    limit: int = Query(1000),
):
    """
    Honeypot: Looks like an admin user data export endpoint.
    Attackers often probe for this to steal user data.
    """
    _log_probe(request, "/admin/export-users", risk_score=80)
    return JSONResponse(
        status_code=403,
        content={
            "error": "Forbidden",
            "message": "This endpoint requires authentication",
            "honeypot_triggered": True,
            "attacker_ip": request.client.host if request.client else "unknown",
            "timestamp": time.time(),
        },
    )


@router.get("/internal/models")
async def root_honeypot_internal_models(request: Request):
    """
    Honeypot: Looks like an internal API that exposes ORM models/schema.
    Attackers probe for this to understand the database structure.
    """
    _log_probe(request, "/internal/models", risk_score=85)
    return JSONResponse(
        status_code=403,
        content={
            "error": "Internal API - Access Denied",
            "honeypot_triggered": True,
            "fake_schema": {
                "message": "This is a decoy. Your IP has been logged.",
            },
        },
    )


@router.get("/config/database")
async def root_honeypot_db_config(request: Request):
    """
    Honeypot: Looks like a database config leak.
    Extremely high-value target for attackers.
    """
    _log_probe(request, "/config/database", risk_score=90)
    return JSONResponse(
        status_code=403,
        content={
            "error": "Access Denied",
            "honeypot_triggered": True,
            "attacker_ip": request.client.host if request.client else "unknown",
        },
    )


@router.get("/.env")
async def honeypot_env_file(request: Request):
    """
    Honeypot: Attackers always probe for .env files.
    """
    _log_probe(request, "/.env", risk_score=95)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "honeypot_triggered": True,
        },
    )


@router.get("/backup.sql")
async def honeypot_backup_sql(request: Request):
    """
    Honeypot: Attackers look for database backup files.
    """
    _log_probe(request, "/backup.sql", risk_score=85)
    return JSONResponse(
        status_code=404,
        content={
            "error": "File Not Found",
            "honeypot_triggered": True,
        },
    )


@router.get("/wp-admin")
async def honeypot_wp_admin(request: Request):
    """
    Honeypot: Catches automated WordPress scanning bots.
    """
    _log_probe(request, "/wp-admin", risk_score=40)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "honeypot_triggered": True,
        },
    )


@router.get("/api-docs")
async def honeypot_api_docs(request: Request):
    """
    Honeypot: Attackers probe for Swagger/OpenAPI docs.
    The real docs are at /docs and /redoc.
    """
    _log_probe(request, "/api-docs", risk_score=30)
    return JSONResponse(
        status_code=404,
        content={
            "error": "API documentation not available at this path",
            "honeypot_triggered": True,
        },
    )


@router.post("/graphql")
async def honeypot_graphql(request: Request):
    """
    Honeypot: Catches GraphQL introspection probes.
    """
    _log_probe(request, "/graphql", risk_score=35)
    return JSONResponse(
        status_code=404,
        content={
            "error": "GraphQL is not enabled",
            "honeypot_triggered": True,
        },
    )


@router.get("/actuator/health")
async def honeypot_actuator(request: Request):
    """
    Honeypot: Spring Boot actuator endpoints are commonly probed.
    """
    _log_probe(request, "/actuator/health", risk_score=25)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "honeypot_triggered": True,
        },
    )


@router.get("/swagger.json")
async def honeypot_swagger_json(request: Request):
    """
    Honeypot: Catches OpenAPI spec probes at common paths.
    """
    _log_probe(request, "/swagger.json", risk_score=20)
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "honeypot_triggered": True,
        },
    )