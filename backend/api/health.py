from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    """
    Returns the operational status of external dependencies.
    """
    return {
        "status": "Operational",
        "dependencies": {
            "Groq": "Configured" if settings.GROQ_API_KEY else "Not Configured",
            "Twilio": "Configured" if all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]) else "Not Configured",
            "SendGrid": "Configured" if settings.SENDGRID_API_KEY else "Not Configured"
        }
    }
