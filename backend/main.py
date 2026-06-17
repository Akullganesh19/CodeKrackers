from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import engine, Base
from .api import auth, analytics, call, fir, evidence, honeypot
from .scheduler import setup_scheduler
import uvicorn
import asyncio
from sqlalchemy import select
from .core.database import engine, Base, AsyncSessionLocal, SessionLocal
from .core.security import get_password_hash
from .models.orm import User
from .core.event_bus import event_bus
import logging

logger = logging.getLogger("vas.main")

# Initialize FastAPI App
app = FastAPI(
    title="VSDP - Vishing & Smishing Defense Platform",
    description="Cybersecurity backend for AI-driven scam detection and forensic reporting.",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(call.router, prefix="/api/call", tags=["call"])
app.include_router(fir.router, prefix="/api/fir", tags=["fir"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["evidence"])
app.include_router(honeypot.router, prefix="/api/honeypot", tags=["honeypot"])

# New Original Routers
from .api import blacklist, canary, childlock, enclave, export, intel, legal, model_guard, openclaw, spam, threats, users, zk_privacy
app.include_router(blacklist.router, prefix="/api/blacklist", tags=["blacklist"])
app.include_router(canary.router, prefix="/api/canary", tags=["canary"])
app.include_router(childlock.router, prefix="/api/childlock", tags=["childlock"])
app.include_router(enclave.router, prefix="/api/enclave", tags=["enclave"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(intel.router, prefix="/api/intel", tags=["intel"])
app.include_router(legal.router, prefix="/api/legal", tags=["legal"])
app.include_router(model_guard.router, prefix="/api/model_guard", tags=["model_guard"])
app.include_router(openclaw.router, prefix="/api/openclaw", tags=["openclaw"])
app.include_router(spam.router, prefix="/api/spam", tags=["spam"])
app.include_router(threats.router, prefix="/api/threats", tags=["threats"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(zk_privacy.router, prefix="/api/zk", tags=["zk_privacy"])

async def handle_spam_blocked(user_id: int, **kwargs):
    """
    Event listener: Increments user's scams_avoided count when spam is blocked.
    Demonstrates Synapse loosely coupled intelligence across systems.
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if user:
                user.scams_avoided = (user.scams_avoided or 0) + 1
                await db.commit()
                logger.info(f"SYNAPSE: Gamification updated. User {user_id} scams_avoided incremented to {user.scams_avoided}.")
    except Exception as e:
        logger.error(f"SYNAPSE ERROR: Failed to increment scams avoided for user {user_id}: {e}")

@app.on_event("startup")
async def startup_event():
    """
    Actions to perform when the server starts:
    1. Create database tables (if they don't exist).
    2. Start the background scheduler.
    """
    # Subscribe to decoupled system events
    event_bus.subscribe('spam.blocked', handle_spam_blocked)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Auto-seed admin user if not exists
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "admin@vsdp.org"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@vsdp.org",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role="admin",
                rbac_level=4
            )
            db.add(admin)
            await db.commit()
            print("Auto-seeded admin user: admin@vsdp.org / admin123")
    
    # setup_scheduler()
    print("VSDP Backend Startup Complete (Scheduler Disabled for Demo).")

@app.get("/")
async def root():
    return {
        "status": "VSDP Backend Operational",
        "version": "2.0.0",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
