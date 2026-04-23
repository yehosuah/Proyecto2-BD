from fastapi.testclient import TestClient

from app.main import create_app


def test_core_health_and_domain_routes_exist():
    client = TestClient(create_app())

    expected = {
        "/health": "ok",
        "/api/auth/health": "auth",
        "/api/catalog/health": "catalog",
        "/api/orders/health": "orders",
        "/api/inventory/health": "inventory",
        "/api/reporting/health": "reporting",
        "/api/admin/health": "admin",
    }

    for path, domain in expected.items():
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "ok"
        assert payload["domain"] == domain
