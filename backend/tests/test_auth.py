def test_verificar_sesion(client, fake_token):
    response = client.get(f"/auth/verificar?token={fake_token}")
    assert response.status_code in (200, 401)
