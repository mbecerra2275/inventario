# ============================================================
# ROUTER DE PRODUCTOS 100% COMPATIBLE CON TU FRONTEND
# SIN Pydantic (ProductoCreate/ProductoOut) porque tu frontend
# trabaja enviando JSON directo con producto.js
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.producto_model import Producto

router = APIRouter(prefix="/productos", tags=["Productos"])


# ------------------------------ DB ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------ SCHEMA (Formulario dinámico) ------------------------------
@router.get("/schema")
def obtener_schema(db: Session = Depends(get_db)):
    columnas = []
    for col in Producto.__table__.columns:
        columnas.append({
            "name": col.name,
            "type": str(col.type)
        })
    return columnas


# ------------------------------ LISTAR PRODUCTOS ------------------------------
@router.get("/")
def obtener_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos


# ------------------------------ PRODUCTOS RECIENTES ------------------------------
@router.get("/recientes")
def productos_recientes(limit: int = 5, db: Session = Depends(get_db)):
    productos = (
        db.query(Producto)
        .order_by(Producto.fecha_creacion.desc())
        .limit(limit)
        .all()
    )
    return productos


# ------------------------------ CREAR PRODUCTO ------------------------------
@router.post("/")
def crear_producto(data: dict, db: Session = Depends(get_db)):
    nuevo = Producto(**data)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ------------------------------ EDITAR PRODUCTO ------------------------------
@router.put("/{id}")
def actualizar_producto(id: int, data: dict, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for key, value in data.items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


# ------------------------------ ELIMINAR PRODUCTO ------------------------------
@router.delete("/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == id).first()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()

    return {"message": "Producto eliminado correctamente"}


