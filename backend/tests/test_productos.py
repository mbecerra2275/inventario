from datetime import datetime

def test_crear_producto(client):
    data = {
        "nombre": "Producto test",
        "clasificacion": "Alimentos",
        "tipo_producto": "Bebida",
        "estado": "Activo",
        "impuestos": 19,
        "codigo_sku": "SKU12345",
        "marca": "Test",
        "precio": 1000,
        "cantidad": 10,
        "fecha_creacion": datetime.now().isoformat(),
        "sucursal_id": 1,
        "costo_neto_unitario": 500,
        "costo_neto_total": 5000,
        "doc_recepcion_ing": "123"
    }
    resp = client.post("/productos/", json=data)
    assert resp.status_code in (200, 201)
