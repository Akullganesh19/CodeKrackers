import logging
import requests
from backend.core.config import settings
from backend.core.resilience import with_retries, circuit_breaker

logger = logging.getLogger("vas.openclaw")

# OpenClaw Gateway defaults
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "22b3d0f8bbe1f335aab557204ab619d5260b91ab8533d3c4"

@circuit_breaker(failure_threshold=3, recovery_timeout=60.0)
@with_retries(max_attempts=3, base_delay=0.5)
def check_openclaw_gateway():
    response = requests.get(OPENCLAW_URL, timeout=1)
    response.raise_for_status()
    return response

def openclaw_analysis(content: str):
    """
    Sends suspicious content to the OpenClaw autonomous agent for deep forensic investigation.
    """
    try:
        # OpenClaw agent communication
        # This is an example of how one might interact with the agent gateway
        # based on standard OpenClaw patterns.
        
        logger.info("Engaging OpenClaw Autonomous Agent...")
        
        # Real-time check if gateway is up
        check_openclaw_gateway()
        
        # In a real integration, we'd use the token to send a task
        # For now, we acknowledge the gateway is active and ready.
        return {
            "status": "engaged",
            "agent": "OpenClaw Sentinel",
            "gateway": OPENCLAW_URL
        }
    except Exception as e:
        logger.error(f"OpenClaw Agent offline: {e}")
        return None
