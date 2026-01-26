from fastapi import Request, HTTPException, status
from orders_service.core.config import settings

async def verify_api_key(request: Request):
    key = request.headers.get("X-API-KEY")
    if key != settings.ORDERS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )