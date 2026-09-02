import httpx
import re
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry

# Use circuit breaker and retry for Honeypot API
honeypot_cb = CircuitBreaker(failure_threshold=4, recovery_timeout=60.0)

@honeypot_cb
@with_retry(max_retries=3, base_delay=0.5, max_delay=3.0, exceptions=(httpx.RequestError,))
async def _call_honeypot_api(url: str, headers: dict, params: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)

async def check_crypto_honeypot(address: str) -> dict:
    """
    Check if a crypto address/token is a honeypot using honeypot.is API.
    """
    api_key = getattr(settings, "HONEYPOT_IS_API_KEY", None)
    if not api_key:
        return {"error": "Honeypot.is API key not configured"}

    url = "https://api.honeypot.is/v2/IsHoneypot"
    headers = {"X-API-KEY": api_key}
    params = {"address": address}

    try:
        result = await _call_honeypot_api(url, headers, params)
        return result
    except httpx.HTTPStatusError as e:
        return {"error": f"API returned status {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
