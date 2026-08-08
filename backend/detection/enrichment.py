
import httpx
from backend.config import settings


async def lookup_ip_reputation(ip: str) -> dict:
    key = settings.ABUSEIPDB_API_KEY
    if key is None:
        return {"skipped": "no ABUSEIPDB_API_KEY configured"}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            "https://api.abuseipdb.com/api/v2/check",
            headers={"Key": key.get_secret_value(), "Accept": "application/json"},
            params={"ipAddress": ip, "maxAgeInDays": 90},
        )
        resp.raise_for_status()
        return resp.json()["data"]