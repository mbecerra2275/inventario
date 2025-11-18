def test_crear_sucursal(client):
    data = {
        "nombre": "Sucursal Test",
        "direccion": "Calle 123",
        "ciudad": "Santiago",
        "telefono": "123456",
        "estado": "Activa",
        "encargado": "Juan",
    }
    resp = client.post("/sucursales/", json=data)
    assert resp.status_code in (200, 201)
