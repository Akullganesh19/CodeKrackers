import httpx
import re
from backend.core.config import settings
from backend.core.resilience import CircuitBreaker, with_retry

def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)


@CircuitBreaker(max_failures=3, reset_timeout=30.0)
@with_retry(max_retries=3, base_delay=0.5)
async def _do_honeypot_request(url: str, headers: dict, params: dict) -> dict:
    """Helper function to execute honeypot request with resilience wrappers."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


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
        return await _do_honeypot_request(url, headers, params)
    except httpx.HTTPStatusError as e:
        return {"error": f"API returned status {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
