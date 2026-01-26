import httpx
from analytics_service.core.config import settings

_async_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient :
    """Dependency-injected async HTTP client."""
    if _async_client is None:
        raise RuntimeError("HTTP client not initialized. Startup event not running?")
    return _async_client


async def init_http_client():
    """Initialize the shared async client (called on startup)."""
    global _async_client
    if _async_client is None:
        _async_client = httpx.AsyncClient(
            timeout=settings.REQUEST_TIMEOUT,
            headers={"X-API-KEY": settings.ORDERS_API_KEY}
        )


async def close_http_client():
    """Close the shared client (called on shutdown)."""
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None