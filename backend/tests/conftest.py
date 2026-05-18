from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


@pytest.fixture
def login_admin(client: TestClient) -> TestClient:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@proyecto2.local", "password": "admin123"},
    )
    assert response.status_code == 200, response.text
    return client


@pytest.fixture
def login_cliente(client: TestClient) -> TestClient:
    response = client.post(
        "/api/auth/login",
        json={"email": "cliente@proyecto2.local", "password": "cliente123"},
    )
    assert response.status_code == 200, response.text
    return client
