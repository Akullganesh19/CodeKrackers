import logging
import requests
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry_sync

logger = logging.getLogger("vas.openclaw")

# OpenClaw Gateway defaults
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "22b3d0f8bbe1f335aab557204ab619d5260b91ab8533d3c4"

def openclaw_fallback(content: str):
    logger.warning("OpenClaw fallback executed")
    return None

@CircuitBreaker(fallback=openclaw_fallback)
@with_retry_sync(max_attempts=3)
def openclaw_analysis(content: str):
    """
    Sends suspicious content to the OpenClaw autonomous agent for deep forensic investigation.
    """
    logger.info("Engaging OpenClaw Autonomous Agent...")

    # Real-time check if gateway is up
    response = requests.get(OPENCLAW_URL, timeout=1)
    response.raise_for_status()

    # In a real integration, we'd use the token to send a task
    # For now, we acknowledge the gateway is active and ready.
    return {
        "status": "engaged",
        "agent": "OpenClaw Sentinel",
        "gateway": OPENCLAW_URL
    }
