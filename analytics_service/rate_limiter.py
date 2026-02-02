import time
import logging

from fastapi import Depends, HTTPException, Request, status

logger = logging.getLogger("analytics.rate_limiter")

REQUEST_LIMIT = 60
WINDOW_SIZE_SECONDS = 60

_rate_limit_store: dict[str, dict[str, float | int]] = {}


def get_api_key(request: Request) -> str:
    """ Extracts API key from request header"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
        )
    
    return api_key

def rate_limit_dependency(api_key: str = Depends(get_api_key)) -> None:
    """
    Fixed window, per API key rate limiter.
    
    Raises HTTP 429 if the request limit is exceeded.
    """
    now = time.time()
    entry = _rate_limit_store.get(api_key)

    # First request from this API key
    if entry is None:
        _rate_limit_store[api_key] = {
            "window_start": now,
            "count": 1,
        }
        return
    window_start = entry["window_start"]
    count = entry["count"]

    # Reset if window expired
    if now - window_start >= WINDOW_SIZE_SECONDS:
        _rate_limit_store[api_key] = {
            "window_start": now,
            "count": 1
        }
        return
    
    count += 1
    entry["count"] = count

    if count > REQUEST_LIMIT:
        logger.warning(
            "Rate limit exceeded for API key=%s (limit=%d per %ds)",
            api_key,
            REQUEST_LIMIT,
            WINDOW_SIZE_SECONDS,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later.",
            headers={
                "Retry-After": str(WINDOW_SIZE_SECONDS)
            }
        )
