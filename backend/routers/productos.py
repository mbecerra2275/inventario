"""
==========================================
Módulo: productos.py
Autor: Milton Becerra
Descripción:
Rutas para CRUD de productos del inventario.
==========================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from backend.database import get_db, Producto

router = APIRouter(prefix="/productos", tags=["Productos"])

# ============================================================
# 📦 MODELOS Pydantic
# ============================================================
from pydantic import BaseModel

class ProductoCreate(BaseModel):
    nombre: str
    clasificacion: Optional[str] = None
    tipo_producto: Optional[str] = None
    estado: str = "Activo"
    impuestos: float = 19.0
    codigo_sku: Optional[str] = None
    marca: Optional[str] = None
    precio: float
    cantidad: int
    sucursal_id: Optional[int] = None

class ProductoResponse(ProductoCreate):
    id: int
    fecha_creacion: datetime
    class Config:
        from_attributes = True

# ============================================================
# 📡 ENDPOINTS
# ============================================================

@router.get("/", response_model=List[ProductoResponse])
def obtener_productos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    productos = db.query(Producto).offset(skip).limit(limit).all()
    return productos


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    if producto.codigo_sku:
        existe = db.query(Producto).filter(Producto.codigo_sku == producto.codigo_sku).first()
        if existe:
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código SKU")

    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, producto: ProductoCreate, db: Session = Depends(get_db)):
    producto_db = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for attr, value in producto.dict().items():
        setattr(producto_db, attr, value)

    db.commit()
    db.refresh(producto_db)
    return producto_db


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}
