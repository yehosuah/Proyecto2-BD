from fastapi.testclient import TestClient
from uuid import uuid4

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


def _unique_email(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}@example.test"


def _login(client: TestClient, email: str, password: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text


def test_client_registration_session_and_logout_flow():
    client = TestClient(create_app())
    email = _unique_email("cliente")

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "nombre": "Cliente",
            "apellido": "Prueba",
            "telefono": "5555-1234",
        },
    )

    assert register_response.status_code == 201, register_response.text
    payload = register_response.json()
    assert payload["user"]["email"] == email
    assert payload["user"]["rol"] == "cliente"

    session_response = client.get("/api/auth/session")
    assert session_response.status_code == 200, session_response.text
    assert session_response.json()["authenticated"] is True

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 204, logout_response.text

    session_after_logout = client.get("/api/auth/session")
    assert session_after_logout.status_code == 200, session_after_logout.text
    assert session_after_logout.json()["authenticated"] is False


def test_admin_can_crud_categories_and_products():
    client = TestClient(create_app())
    _login(client, "admin@proyecto2.local", "admin123")

    category_name = f"Categoria {uuid4().hex[:6]}"
    category_response = client.post(
        "/api/admin/categories",
        json={"nombre": category_name, "descripcion": "Categoria temporal", "activa": True},
    )
    assert category_response.status_code == 201, category_response.text
    category = category_response.json()

    product_sku = f"SKU-{uuid4().hex[:8].upper()}"
    product_response = client.post(
        "/api/admin/products",
        json={
            "id_categoria": category["id_categoria"],
            "id_proveedor": None,
            "sku": product_sku,
            "nombre": "Producto temporal",
            "descripcion": "Producto creado por prueba",
            "precio_unitario": 99.5,
            "stock_actual": 14,
            "activo": True,
        },
    )
    assert product_response.status_code == 201, product_response.text
    product = product_response.json()

    list_response = client.get("/api/admin/products")
    assert list_response.status_code == 200, list_response.text
    assert any(item["sku"] == product_sku for item in list_response.json()["items"])

    update_response = client.put(
        f"/api/admin/products/{product['id_producto']}",
        json={
            "id_categoria": category["id_categoria"],
            "id_proveedor": None,
            "sku": product_sku,
            "nombre": "Producto actualizado",
            "descripcion": "Descripcion actualizada",
            "precio_unitario": 109.0,
            "stock_actual": 18,
            "activo": True,
        },
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["nombre"] == "Producto actualizado"

    delete_product = client.delete(f"/api/admin/products/{product['id_producto']}")
    assert delete_product.status_code == 204, delete_product.text

    delete_category = client.delete(f"/api/admin/categories/{category['id_categoria']}")
    assert delete_category.status_code == 204, delete_category.text


def test_checkout_paths_history_and_sales_report_export():
    client = TestClient(create_app())
    email = _unique_email("comprador")

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "secret123",
            "nombre": "Comprador",
            "apellido": "Demo",
            "telefono": "5555-3333",
        },
    )
    assert register_response.status_code == 201, register_response.text

    catalog_response = client.get("/api/catalog/products")
    assert catalog_response.status_code == 200, catalog_response.text
    product = catalog_response.json()["items"][0]
    initial_stock = product["stock_actual"]

    rejected_checkout = client.post(
        "/api/orders/checkout",
        json={
            "customer": {
                "nombre": "Comprador Demo",
                "email": email,
                "telefono": "5555-3333",
            },
            "tipo_entrega": "pickup",
            "nota_cliente": "Pago debe ser rechazado",
            "items": [{"id_producto": product["id_producto"], "cantidad": 1}],
            "payment": {"metodo": "tarjeta", "referencia": "FAIL-0000"},
        },
    )
    assert rejected_checkout.status_code == 409, rejected_checkout.text
    rejected_payload = rejected_checkout.json()
    assert rejected_payload["payment"]["estado"] == "rechazado"

    product_after_reject = client.get(f"/api/catalog/products/{product['sku']}")
    assert product_after_reject.status_code == 200, product_after_reject.text
    assert product_after_reject.json()["stock_actual"] == initial_stock

    approved_checkout = client.post(
        "/api/orders/checkout",
        json={
            "customer": {
                "nombre": "Comprador Demo",
                "email": email,
                "telefono": "5555-3333",
            },
            "tipo_entrega": "pickup",
            "nota_cliente": "Pago aprobado",
            "items": [{"id_producto": product["id_producto"], "cantidad": 1}],
            "payment": {"metodo": "efectivo", "referencia": "EFECTIVO-OK"},
        },
    )
    assert approved_checkout.status_code == 201, approved_checkout.text
    approved_payload = approved_checkout.json()
    assert approved_payload["payment"]["estado"] == "aprobado"

    history_response = client.get("/api/orders/me")
    assert history_response.status_code == 200, history_response.text
    assert any(
        order["codigo_publico"] == approved_payload["order"]["codigo_publico"]
        for order in history_response.json()["items"]
    )

    admin_client = TestClient(create_app())
    _login(admin_client, "admin@proyecto2.local", "admin123")

    sales_report = admin_client.get("/api/admin/reports/sales")
    assert sales_report.status_code == 200, sales_report.text
    assert "series" in sales_report.json()

    csv_export = admin_client.get("/api/admin/reports/sales/export.csv")
    assert csv_export.status_code == 200, csv_export.text
    assert csv_export.headers["content-type"].startswith("text/csv")
    assert "fecha" in csv_export.text.lower()
