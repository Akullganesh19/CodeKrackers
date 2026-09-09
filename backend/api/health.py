from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.core.database import get_db
from backend.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check(db: AsyncSession = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "dependencies": {
            "database": "unknown",
            "twilio": "configured" if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]) else "unconfigured",
            "groq": "configured" if settings.GROQ_API_KEY else "unconfigured",
            "sendgrid": "configured" if settings.SENDGRID_API_KEY else "unconfigured"
        }
    }

    try:
        await db.execute(text("SELECT 1"))
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)

    return health_status
