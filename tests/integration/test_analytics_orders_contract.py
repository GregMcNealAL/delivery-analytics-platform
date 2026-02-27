import asyncio

import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import analytics_service.rate_limiter as rate_limiter
import orders_service.main as orders_main
from analytics_service.core.config import settings as analytics_settings
from analytics_service.core.http_client import get_http_client
from analytics_service.routers.analytics import router as analytics_router
from orders_service.core.config import settings as orders_settings
from orders_service.db import Base
from orders_service.models import Order


def _build_analytics_client(orders_client: httpx.AsyncClient):
    app = FastAPI()
    app.include_router(analytics_router)

    async def override_http_client():
        return orders_client

    app.dependency_overrides[get_http_client] = override_http_client
    return TestClient(app)


def _setup_orders_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    return engine, testing_session_local


def _override_orders_db(testing_session_local):
    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    orders_main.app.dependency_overrides[orders_main.get_db] = override_get_db


def test_summary_real_cross_service_success(monkeypatch):
    engine, testing_session_local = _setup_orders_db()
    _override_orders_db(testing_session_local)

    session = testing_session_local()
    session.add_all(
        [
            Order(item_name="A", location="Austin", cost=10.0, delivery_time=30, status="delivered"),
            Order(item_name="B", location="Dallas", cost=20.0, delivery_time=50, status="delivered"),
        ]
    )
    session.commit()
    session.close()

    monkeypatch.setattr(orders_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_URL", "http://orders.local/orders")
    rate_limiter._rate_limit_store.clear()

    orders_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=orders_main.app),
        headers={"X-API-KEY": "shared-key"},
    )
    analytics_client = _build_analytics_client(orders_client)

    with analytics_client:
        response = analytics_client.get("/analytics/summary", headers={"X-API-Key": "shared-key"})

    asyncio.run(orders_client.aclose())
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    assert response.status_code == 200
    assert response.json() == {
        "total_orders": 2,
        "average_delivery_time": 40.0,
        "average_cost": 15.0,
        "top_locations": ["Austin", "Dallas"],
    }


def test_summary_real_cross_service_upstream_auth_failure(monkeypatch):
    engine, testing_session_local = _setup_orders_db()
    _override_orders_db(testing_session_local)

    monkeypatch.setattr(orders_settings, "ORDERS_API_KEY", "orders-secret")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_KEY", "analytics-secret")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_URL", "http://orders.local/orders")
    monkeypatch.setattr(analytics_settings, "MAX_RETRIES", 1)
    rate_limiter._rate_limit_store.clear()

    orders_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=orders_main.app),
        headers={"X-API-KEY": "analytics-secret"},
    )
    analytics_client = _build_analytics_client(orders_client)

    with analytics_client:
        response = analytics_client.get("/analytics/summary", headers={"X-API-Key": "analytics-secret"})

    asyncio.run(orders_client.aclose())
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    assert response.status_code == 502
    assert response.json()["detail"] == "Orders service authentication failed"


def test_summary_real_cross_service_upstream_404(monkeypatch):
    engine, testing_session_local = _setup_orders_db()
    _override_orders_db(testing_session_local)

    monkeypatch.setattr(orders_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_URL", "http://orders.local/does-not-exist")
    monkeypatch.setattr(analytics_settings, "MAX_RETRIES", 1)
    rate_limiter._rate_limit_store.clear()

    orders_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=orders_main.app),
        headers={"X-API-KEY": "shared-key"},
    )
    analytics_client = _build_analytics_client(orders_client)

    with analytics_client:
        response = analytics_client.get("/analytics/summary", headers={"X-API-Key": "shared-key"})

    asyncio.run(orders_client.aclose())
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    assert response.status_code == 502
    assert response.json()["detail"] == "Orders service returned status: 404"


def test_status_breakdown_real_cross_service_success(monkeypatch):
    engine, testing_session_local = _setup_orders_db()
    _override_orders_db(testing_session_local)

    session = testing_session_local()
    session.add_all(
        [
            Order(item_name="A", location="Austin", cost=10.0, delivery_time=30, status="delivered"),
            Order(item_name="B", location="Dallas", cost=20.0, delivery_time=50, status="pending"),
            Order(item_name="C", location="Austin", cost=15.0, delivery_time=40, status="delivered"),
            Order(item_name="D", location="Miami", cost=22.0, delivery_time=60, status="cancelled"),
        ]
    )
    session.commit()
    session.close()

    monkeypatch.setattr(orders_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_URL", "http://orders.local/orders")
    rate_limiter._rate_limit_store.clear()

    orders_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=orders_main.app),
        headers={"X-API-KEY": "shared-key"},
    )
    analytics_client = _build_analytics_client(orders_client)

    with analytics_client:
        response = analytics_client.get("/analytics/status-breakdown", headers={"X-API-Key": "shared-key"})

    asyncio.run(orders_client.aclose())
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    assert response.status_code == 200
    assert response.json() == {
        "statuses": {
            "delivered": 2,
            "pending": 1,
            "cancelled": 1,
        }
    }


def test_location_breakdown_real_cross_service_success(monkeypatch):
    engine, testing_session_local = _setup_orders_db()
    _override_orders_db(testing_session_local)

    session = testing_session_local()
    session.add_all(
        [
            Order(item_name="A", location="Austin", cost=10.0, delivery_time=30, status="delivered"),
            Order(item_name="B", location="Dallas", cost=20.0, delivery_time=50, status="pending"),
            Order(item_name="C", location="Austin", cost=15.0, delivery_time=40, status="delivered"),
            Order(item_name="D", location="Miami", cost=22.0, delivery_time=60, status="cancelled"),
        ]
    )
    session.commit()
    session.close()

    monkeypatch.setattr(orders_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_KEY", "shared-key")
    monkeypatch.setattr(analytics_settings, "ORDERS_API_URL", "http://orders.local/orders")
    rate_limiter._rate_limit_store.clear()

    orders_client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=orders_main.app),
        headers={"X-API-KEY": "shared-key"},
    )
    analytics_client = _build_analytics_client(orders_client)

    with analytics_client:
        response = analytics_client.get(
            "/analytics/location-breakdown?limit=2",
            headers={"X-API-Key": "shared-key"},
        )

    asyncio.run(orders_client.aclose())
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    assert response.status_code == 200
    assert response.json() == {
        "top_locations": [
            {"location": "Austin", "count": 2},
            {"location": "Dallas", "count": 1},
        ]
    }
