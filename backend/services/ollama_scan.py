import json
import logging
from typing import Any, Dict

import requests

from backend.core.resilience import circuit_breaker, with_retries

logger = logging.getLogger("vas.ollama")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  # Upgraded for tool-calling support


@with_retries(max_attempts=2, base_delay=0.2)
@circuit_breaker(failure_threshold=5, recovery_timeout=60.0)
def _call_ollama_api(payload: dict) -> dict:
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    response.raise_for_status()  # Raise error for bad status codes so retries can catch it
    return response.json()


def ollama_deep_scan(content: str, source_type: str = "sms") -> Dict[str, Any]:
    """
    Uses local Ollama instance for on-device/private threat analysis.
    """
    try:
        prompt = f"""
        Analyze this {source_type} for scam/phishing intent.
        Content: "{content}"
        
        Respond ONLY with a JSON object:
        {{
            "is_scam": boolean,
            "confidence": float (0.0 to 1.0),
            "reason": "short summary",
            "risk_factors": ["list"]
        }}
        """

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }

        try:
            response_json = _call_ollama_api(payload)
            result = response_json.get("response", "{}")
            data = json.loads(result)

            return {
                "score_increase": (
                    round(data.get("confidence", 0.0), 2)
                    if data.get("is_scam")
                    else 0.0
                ),
                "reason": data.get("reason", "Local AI Analysis complete"),
                "risk_factors": data.get("risk_factors", []),
            }
        except Exception as e:
            logger.warning(f"Ollama service call failed: {e}")
            raise e  # re-raise to be caught by outer try-except and return default fallback

    except Exception as e:
        logger.error(f"Ollama Scan Error: {e}")
        return {"score_increase": 0.0, "reason": "Local AI Scan failed"}
