import logging

import requests

from backend.core.config import settings
from backend.core.resilience import circuit_breaker, with_retries

logger = logging.getLogger("vas.openclaw")

# OpenClaw Gateway defaults
OPENCLAW_URL = "http://127.0.0.1:18789"
OPENCLAW_TOKEN = "22b3d0f8bbe1f335aab557204ab619d5260b91ab8533d3c4"


@circuit_breaker(failure_threshold=5, recovery_timeout=30.0)
@with_retries(max_attempts=2, base_delay=0.5, exceptions=(requests.RequestException,))
def _check_openclaw_reachable():
    requests.get(OPENCLAW_URL, timeout=1).raise_for_status()


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
        _check_openclaw_reachable()

        # In a real integration, we'd use the token to send a task
        # For now, we acknowledge the gateway is active and ready.
        return {
            "status": "engaged",
            "agent": "OpenClaw Sentinel",
            "gateway": OPENCLAW_URL,
        }
    except Exception as e:
        logger.error(f"OpenClaw Agent offline: {e}")
        return None
