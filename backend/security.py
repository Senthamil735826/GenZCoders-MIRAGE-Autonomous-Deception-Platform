
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from backend.config import settings

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    
    if api_key != settings.MIRAGE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key. Access denied.",
        )
    return api_key