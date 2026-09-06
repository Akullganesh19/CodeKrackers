from fastapi import APIRouter
from backend.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    """
    Health check endpoint returning status of all dependencies.
    Used by load balancers and monitoring.
    """
    # Evaluate configured capabilities as a proxy for external dependency readiness
    dependencies = {
        "groq_api": "configured" if settings.GROQ_API_KEY else "disabled",
        "twilio_api": "configured" if settings.TWILIO_ACCOUNT_SID else "disabled",
        "honeypot_api": "configured" if settings.HONEYPOT_IS_API_KEY else "disabled",
        "sendgrid_api": "configured" if settings.SENDGRID_API_KEY else "disabled",
    }

    status = "operational"

    return {
        "status": status,
        "dependencies": dependencies
    }
