def test_exportar_csv(client):
    resp = client.get("/informes/exportar/csv?token=fake")
    assert resp.status_code in (200, 401)
