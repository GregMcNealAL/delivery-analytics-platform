from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import orders_service.main as orders_main
from orders_service.core.config import settings as orders_settings
from orders_service.db import Base
from orders_service.models import Order


def _build_orders_test_client(api_key: str = "test-key"):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    orders_main.app.dependency_overrides[orders_main.get_db] = override_get_db
    orders_settings.ORDERS_API_KEY = api_key
    client = TestClient(orders_main.app)
    return client, testing_session_local, engine


def _cleanup_orders_test_client(engine):
    orders_main.app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def test_orders_create_update_delete_require_api_key():
    client, _session_local, engine = _build_orders_test_client()
    try:
        create_resp = client.post(
            "/orders",
            json={
                "item_name": "Widget",
                "location": "Austin",
                "cost": 25.5,
                "delivery_time": 45,
                "status": "pending",
            },
        )
        assert create_resp.status_code == 401

        update_resp = client.patch(
            "/orders/1",
            json={"status": "delivered"},
        )
        assert update_resp.status_code == 401

        delete_resp = client.delete("/orders/1")
        assert delete_resp.status_code == 401
    finally:
        _cleanup_orders_test_client(engine)


def test_orders_create_validates_required_fields():
    client, _session_local, engine = _build_orders_test_client()
    try:
        response = client.post(
            "/orders",
            headers={"X-API-Key": "test-key"},
            json={
                "item_name": "Widget",
                "location": "Austin",
                "cost": 25.5,
                "delivery_time": 45,
            },
        )
        assert response.status_code == 422
    finally:
        _cleanup_orders_test_client(engine)


def test_orders_update_validates_field_type():
    client, session_local, engine = _build_orders_test_client()
    try:
        session = session_local()
        session.add(
            Order(
                item_name="Seed",
                location="Austin",
                cost=11.0,
                delivery_time=30,
                status="pending",
            )
        )
        session.commit()
        session.close()

        response = client.patch(
            "/orders/1",
            headers={"X-API-Key": "test-key"},
            json={"delivery_time": "not-an-int"},
        )
        assert response.status_code == 422
    finally:
        _cleanup_orders_test_client(engine)


def test_orders_create_update_delete_contract():
    client, _session_local, engine = _build_orders_test_client()
    try:
        create_resp = client.post(
            "/orders",
            headers={"X-API-Key": "test-key"},
            json={
                "item_name": "Widget",
                "location": "Austin",
                "cost": 25.5,
                "delivery_time": 45,
                "status": "pending",
            },
        )
        assert create_resp.status_code == 200
        created = create_resp.json()
        assert created["item_name"] == "Widget"
        assert created["status"] == "pending"

        order_id = created["id"]
        update_resp = client.patch(
            f"/orders/{order_id}",
            headers={"X-API-Key": "test-key"},
            json={"status": "delivered"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["status"] == "delivered"

        delete_resp = client.delete(
            f"/orders/{order_id}",
            headers={"X-API-Key": "test-key"},
        )
        assert delete_resp.status_code == 200
        assert delete_resp.json()["message"] == "Item deleted successfully"
    finally:
        _cleanup_orders_test_client(engine)
