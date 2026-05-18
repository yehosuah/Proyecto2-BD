from fastapi.testclient import TestClient


def test_admin_endpoint_allows_admin(login_admin: TestClient):
    response = login_admin.get('/api/admin/products')
    assert response.status_code == 200, response.text


def test_admin_endpoint_denies_cliente_with_403(login_cliente: TestClient):
    response = login_cliente.get('/api/admin/products')
    assert response.status_code == 403, response.text


def test_inventory_adjustment_denies_cliente_with_403(login_cliente: TestClient):
    response = login_cliente.post(
        '/api/inventory/adjustments',
        json={'id_producto': 1, 'cantidad_delta': 1, 'motivo': 'Prueba no permitida'},
    )
    assert response.status_code == 403, response.text


def test_reporting_snapshot_denies_unauthenticated_with_401(client: TestClient):
    response = client.get('/api/reporting/snapshot')
    assert response.status_code == 401, response.text
