from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.api.v1.api import api_router
from backend.core.config import settings
from backend.core.ws import manager
from backend.core.middleware import (
    SecurityHeadersMiddleware,
    AuditLogMiddleware,
    InputSanitizationMiddleware,
    RAPSMiddleware,
)
from backend.core.limiter import limiter
from backend.db.session import get_db
from backend.services.canary_service import plant_seed_tokens
from backend.core.logger import setup_logging, get_logger

# ─── Logging ───
setup_logging(json_logs=False) # Switch to True in production for ELK/Datadog
logger = get_logger("vas.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("VAS Defense System starting up...")
    logger.info("Database URL configured", database_snippet=settings.DATABASE_URL[:30] + "...")
    logger.info("Service integrations", groq_ai="ACTIVE" if settings.GROQ_API_KEY else "DISABLED", twilio="ACTIVE" if settings.TWILIO_ACCOUNT_SID else "DISABLED")

    # ─── Seed Canary Tokens on Startup ───
    try:
        db = next(get_db())
        plant_seed_tokens(db)
        db.close()
    except Exception as e:
        logger.warning("Could not seed canary tokens (DB may not be ready)", error=str(e))

    yield
    logger.info("VAS Defense System shutting down...")


import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    root_path="/api" if os.environ.get("VERCEL") else "",
    docs_url="/docs",
    redoc_url="/redoc",
    version="2.1.0",
    description="AI-powered national cybersecurity infrastructure for vishing & smishing defense.",
)

@app.middleware("http")
async def diagnostic_logging(request: Request, call_next):
    logger.info("INCOMING REQUEST", path=request.url.path, method=request.method, root_path=request.scope.get("root_path"))
    response = await call_next(request)
    return response

# ─── Rate Limiter ───
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Security Middleware Stack (order matters: outermost runs first) ───
app.add_middleware(InputSanitizationMiddleware)   # 1. Basic WAF pattern blocking
app.add_middleware(RAPSMiddleware)                # 2. RASP - real-time attack detection & blocking
app.add_middleware(AuditLogMiddleware)            # 3. Immutable audit logging
app.add_middleware(SecurityHeadersMiddleware)     # 4. Response header hardening

# ─── CORS ───
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-Response-Time"],
    )

# ─── WebSocket ───
@app.websocket("/ws/threats")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ─── Routes ───
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root() -> dict:
    return {
        "system": "VAS Intelligence Portal",
        "version": "2.1.0",
        "status": "operational",
        "docs": "/docs",
        "defense_layers": ["smishing", "vishing", "honeypot", "legal", "analytics"],
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
        "ai_engine": "groq-llama3",
        "defense_active": True,
    }
