import httpx
from backend.core.resilience import CircuitBreaker, with_retry
import re
from backend.core.config import settings

def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)


@CircuitBreaker(failure_threshold=3, recovery_timeout=60)
@with_retry(max_attempts=3, initial_backoff=0.5)
async def _fetch_crypto_api(url, headers, params):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
        return {"error": f"API returned status {response.status_code}"}

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
        return await _fetch_crypto_api(url, headers, params)
    except Exception as e:
        return {"error": str(e)}
