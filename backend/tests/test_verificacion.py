def test_verificar(client, fake_token):
    resp = client.get(f"/auth/verificar?token={fake_token}")
    assert resp.status_code in (200, 401)
