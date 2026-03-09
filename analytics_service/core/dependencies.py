from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from analytics_service.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(key: str | None = Security(api_key_header)) -> str:
    if key != settings.ORDERS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return key
