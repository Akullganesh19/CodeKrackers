import httpx
import re
from backend.core.config import settings
from backend.core.resilience import with_retries, circuit_breaker


def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)


@circuit_breaker(max_failures=3, reset_timeout=30)
@with_retries(
    max_attempts=3,
    base_delay=0.5,
    exceptions=(httpx.RequestError, httpx.HTTPStatusError),
)
async def check_crypto_honeypot(address: str) -> dict:
    """
    Check if a crypto address/token is a honeypot using honeypot.is API.
    Raises exceptions on failure to trigger retries/circuit breaker.
    """
    api_key = getattr(settings, "HONEYPOT_IS_API_KEY", None)
    if not api_key:
        # Cannot proceed without an API key; no point in retrying this.
        raise ValueError("Honeypot.is API key not configured")

    url = "https://api.honeypot.is/v2/IsHoneypot"
    headers = {"X-API-KEY": api_key}
    params = {"address": address}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
