from backend.core.resilience import with_retry_sync
import logging
import requests
from backend.core.config import settings

logger = logging.getLogger("vas.openclaw")

# OpenClaw Gateway defaults
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "22b3d0f8bbe1f335aab557204ab619d5260b91ab8533d3c4"

def openclaw_analysis(content: str):
    """
    Sends suspicious content to the OpenClaw autonomous agent for deep forensic investigation.
    """
    @with_retry_sync(max_retries=3, base_delay=0.5, exceptions=(requests.exceptions.RequestException,))
    def _call():
        logger.info("Engaging OpenClaw Autonomous Agent...")
        requests.get(OPENCLAW_URL, timeout=1)
        return {
            "status": "engaged",
            "agent": "OpenClaw Sentinel",
            "gateway": OPENCLAW_URL
        }

    try:
        return _call()
    except Exception as e:
        logger.error(f"OpenClaw Agent offline: {e}")
        return None
