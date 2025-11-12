from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from typing import List
from app.database.connection import SessionLocal, engine
from app.models.producto_model import Producto


from app.schemas.producto_schema import ProductoCreate, ProductoOut

router = APIRouter(prefix="/productos", tags=["Productos"])

# Dependencia de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- LISTAR PRODUCTOS ----------
@router.get("/", response_model=List[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos


# ---------- CREAR NUEVO PRODUCTO ----------
@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


# ---------- ACTUALIZAR PRODUCTO ----------
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, datos: ProductoCreate, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for campo, valor in datos.dict().items():
        setattr(producto, campo, valor)
    db.commit()
    db.refresh(producto)
    return producto


# ---------- ELIMINAR PRODUCTO ----------
@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}


# ---------- OBTENER ESQUEMA DE TABLA ----------
@router.get("/schema")
def obtener_esquema_productos():
    insp = inspect(engine)
    columnas = []
    for col in insp.get_columns("productos"):
        columnas.append({
            "name": col["name"],
            "type": str(col["type"]),
            "nullable": col["nullable"],
            "default": col["default"]
        })
    return columnas
