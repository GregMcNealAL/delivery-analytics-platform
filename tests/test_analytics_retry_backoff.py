import asyncio

import httpx
import pytest
from fastapi import HTTPException

import analytics_service.routers.analytics as analytics_router
from analytics_service.core.config import settings


def test_fetch_orders_retries_with_exponential_backoff(monkeypatch):
    attempts = {"count": 0}
    sleep_calls = []

    def failing_handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        raise httpx.ConnectError("connection refused", request=request)

    async def fake_sleep(delay: float):
        sleep_calls.append(delay)

    monkeypatch.setattr(settings, "ORDERS_API_URL", "http://orders.local/orders")
    monkeypatch.setattr(settings, "MAX_RETRIES", 4)
    monkeypatch.setattr(settings, "INITIAL_BACKOFF", 0.25)
    monkeypatch.setattr(analytics_router.asyncio, "sleep", fake_sleep)

    client = httpx.AsyncClient(transport=httpx.MockTransport(failing_handler))

    with pytest.raises(HTTPException) as exc:
        asyncio.run(analytics_router.fetch_orders(client))

    asyncio.run(client.aclose())

    assert exc.value.status_code == 502
    assert "Orders service network error" in exc.value.detail
    assert attempts["count"] == 4
    assert sleep_calls == [0.25, 0.5, 1.0]
