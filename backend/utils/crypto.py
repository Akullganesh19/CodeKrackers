import httpx
import re
from backend.core.config import settings
from backend.core.resilience import async_with_retries

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

    @async_with_retries(max_attempts=3, initial_delay=0.1)
    async def _call_honeypot_api():
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()

    try:
        return await _call_honeypot_api()
    except httpx.HTTPStatusError as e:
        return {"error": f"API returned status {e.response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
