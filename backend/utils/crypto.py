import re

import httpx

from backend.core.config import settings
from backend.core.resilience import async_with_retries


@async_with_retries(max_attempts=3, base_delay=0.5, exceptions=(Exception,))
async def _call_crypto_api(client, url, headers, params):
    return await client.get(url, headers=headers, params=params)


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

    async with httpx.AsyncClient() as client:
        try:
            response = await _call_crypto_api(client, url, headers, params)
            if response.status_code == 200:
                return response.json()
            return {"error": f"API returned status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
