import re

import httpx

from backend.core.config import settings
from backend.core.resilience import (
    CircuitBreaker,
    CircuitBreakerOpenException,
    with_retry_async,
)

crypto_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=60.0)


def extract_crypto_addresses(text: str) -> list[str]:
    """
    Extract EVM (Ethereum-style) addresses from text.
    """
    pattern = r"0x[a-fA-F0-9]{40}"
    return re.findall(pattern, text)


@crypto_cb
@with_retry_async(max_attempts=3, base_delay=1.0)
async def _fetch_crypto_honeypot(url, headers, params):
    async with httpx.AsyncClient(timeout=5.0) as client:
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
        return await _fetch_crypto_honeypot(url, headers, params)
    except CircuitBreakerOpenException:
        return {"error": "Honeypot API is down (Circuit Breaker OPEN)"}
    except Exception as e:
        return {"error": f"Failed to check honeypot after retries: {str(e)}"}
