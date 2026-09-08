from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    """
    Returns the operational status of external dependencies based on whether their keys are configured.
    """
    return {
        "status": "healthy",
        "dependencies": {
            "groq": "configured" if settings.GROQ_API_KEY else "disabled",
            "twilio": "configured" if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN else "disabled",
            "sendgrid": "configured" if settings.SENDGRID_API_KEY else "disabled"
        }
    }
