# backend/test_db.py
from backend.database import SessionLocal, Producto

# Crear una sesión
db = SessionLocal()

try:
    # ============================================================
    # ➕ 1. Insertar un producto de prueba
    # ============================================================
    nuevo_producto = Producto(
        nombre="Coca-Cola 350ml",
        clasificacion="Bebida",
        tipo_producto="Gaseosa",
        estado="Activo",
        impuestos=19.0,
        codigo_sku="CC350",
        marca="Coca-Cola",
        precio=1000.0,
        cantidad=50
    )

    db.add(nuevo_producto)
    db.commit()
    print("✅ Producto de prueba agregado correctamente.")

    # ============================================================
    # 📋 2. Listar todos los productos
    # ============================================================
    print("\n📦 Lista de productos registrados:")
    productos = db.query(Producto).all()
    for p in productos:
        print(f"   ID: {p.id} | Nombre: {p.nombre} | Precio: {p.precio} | Cantidad: {p.cantidad}")

    # ============================================================
    # ✏️ 3. Editar el producto recién agregado
    # ============================================================
    producto = db.query(Producto).filter_by(codigo_sku="CC350").first()
    if producto:
        producto.precio = 1200.0
        producto.cantidad = 45
        db.commit()
        print(f"\n✏️ Producto actualizado: {producto.nombre} → ${producto.precio} ({producto.cantidad} unidades)")

    # ============================================================
    # ❌ 4. Eliminar producto (opcional)
    # ============================================================
    # db.delete(producto)
    # db.commit()
    # print(f"\n🗑️ Producto eliminado: {producto.nombre}")

except Exception as e:
    db.rollback()
    print(f"❌ Error durante la operación: {e}")

finally:
    db.close()
