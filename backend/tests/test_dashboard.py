def test_metricas(client):
    resp = client.get("/dashboard/metricas")
    assert resp.status_code == 200
    assert "total_productos" in resp.json()


def test_distribucion_categorias(client):
    resp = client.get("/dashboard/categorias/distribucion")
    assert resp.status_code == 200


def test_sucursales_activas(client):
    resp = client.get("/dashboard/sucursales/activas")
    assert resp.status_code == 200
