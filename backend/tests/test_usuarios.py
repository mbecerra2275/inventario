def test_crear_usuario(client):
    data = {
        "nombre": "Test User",
        "correo": "test@example.com",
        "password": "123456",
        "rol": "Admin"
    }

    resp = client.post("/usuarios/registro", data=data)

    assert resp.status_code in (200, 201)
    json = resp.json()
    assert json["correo"] == "test@example.com"
    assert json["rol"] == "Admin"
