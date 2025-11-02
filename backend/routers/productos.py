# backend/routers/productos.py
"""
=========================================================
Módulo: productos.py (v2)
Autor: Milton Becerra
Descripción:
CRUD completo de productos con relación a sucursales.
=========================================================
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from backend.database import get_db, Producto, Sucursal

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

# ---------------------------------------------------------
# 📦 Esquemas Pydantic
# ---------------------------------------------------------
class ProductoBase(BaseModel):
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


class ProductoResponse(ProductoBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# 📡 ENDPOINTS
# ---------------------------------------------------------

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    return productos


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED)
def crear_producto(data: ProductoBase, db: Session = Depends(get_db)):
    # ✅ validar sucursal si viene
    if data.sucursal_id:
        suc = db.query(Sucursal).filter(Sucursal.id == data.sucursal_id).first()
        if not suc:
            raise HTTPException(status_code=400, detail="Sucursal no válida")

    nuevo = Producto(**data.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, data: ProductoBase, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # si viene sucursal, validar
    if data.sucursal_id:
        suc = db.query(Sucursal).filter(Sucursal.id == data.sucursal_id).first()
        if not suc:
            raise HTTPException(status_code=400, detail="Sucursal no válida")

    for key, value in data.dict().items():
        setattr(producto, key, value)

    db.commit()
    db.refresh(producto)
    return producto


@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    db.delete(producto)
    db.commit()
    return {"message": "Producto eliminado correctamente"}
