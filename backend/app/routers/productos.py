# ============================================================
# 📦 ROUTER DE PRODUCTOS  
# Módulo encargado de la administración de productos
# Compatible con el frontend actual
# Incluye control de acceso por roles  
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.producto_model import Producto
from app.auth.auth import rol_requerido   # 🔐 Middleware de autorización

# ============================================================
# 📁 Configuración del Router
# ============================================================
router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# ============================================================
# 🔌 Conexión a la Base de Datos
# ============================================================
def get_db():
    """
    🔄 Provee una sesión de base de datos por solicitud.
    Cierra automáticamente después de usarla.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 📘 1. OBTENER SCHEMA DE LA TABLA PRODUCTOS
# Roles permitidos: admin, bodega, sucursal
# ============================================================
@router.get(
    "/schema",
    dependencies=[Depends(rol_requerido(["admin", "bodega", "sucursal"]))]
)
def obtener_schema(db: Session = Depends(get_db)):
    """
    📄 Devuelve un listado con las columnas del modelo Producto, 
    útil para construir plantillas dinámicas en el frontend.
    """
    columnas = []
    for col in Producto.__table__.columns:
        columnas.append({
            "name": col.name,
            "type": str(col.type)
        })
    return columnas


# ============================================================
# 📘 2. LISTAR TODOS LOS PRODUCTOS
# Roles permitidos: admin, bodega, sucursal
# ============================================================
@router.get(
    "/", 
    dependencies=[Depends(rol_requerido(["admin", "bodega", "sucursal"]))]
)
def obtener_productos(db: Session = Depends(get_db)):
    """
    📋 Obtiene todos los productos registrados en la base de datos.
    """
    productos = db.query(Producto).all()
    return productos


# ============================================================
# 📘 3. LISTAR PRODUCTOS RECIENTES
# Roles permitidos: admin, bodega, sucursal
# ============================================================
@router.get(
    "/recientes",
    dependencies=[Depends(rol_requerido(["admin", "bodega", "sucursal"]))]
)
def productos_recientes(limit: int = 5, db: Session = Depends(get_db)):
    """
    🕒 Devuelve los últimos 'limit' productos creados.
    Usado en el dashboard.
    """
    productos = (
        db.query(Producto)
        .order_by(Producto.fecha_creacion.desc())
        .limit(limit)
        .all()
    )
    return productos


# ============================================================
# 🟢 4. CREAR PRODUCTO
# Roles permitidos: admin, bodega
# ============================================================
@router.post(
    "/",
    dependencies=[Depends(rol_requerido(["admin", "bodega"]))]
)
def crear_producto(data: dict, db: Session = Depends(get_db)):
    """
    ➕ Crea un nuevo producto en la base de datos.
    """
    nuevo = Producto(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ============================================================
# 🟡 5. ACTUALIZAR PRODUCTO
# Roles permitidos: admin
# ============================================================
@router.put(
    "/{id}",
    dependencies=[Depends(rol_requerido(["admin"]))]
)
def actualizar_producto(id: int, data: dict, db: Session = Depends(get_db)):
    """
    ✏️ Actualiza los datos de un producto existente.
    """
    producto = db.query(Producto).filter(Producto.id == id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Actualizar propiedades dinámicamente
    for key, value in data.items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


# ============================================================
# 🔴 6. ELIMINAR PRODUCTO
# Roles permitidos: admin
# ============================================================
@router.delete(
    "/{id}",
    dependencies=[Depends(rol_requerido(["admin"]))]
)
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    """
    🗑️ Elimina un producto por ID.
    """
    producto = db.query(Producto).filter(Producto.id == id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()

    return {"message": "Producto eliminado correctamente"}
