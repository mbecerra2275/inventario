"""
==========================================
Módulo: sucursales.py
Autor: Milton Becerra
Descripción:
Rutas para la gestión de sucursales del sistema.
==========================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from backend.database import get_db, Sucursal, Producto
from pydantic import BaseModel

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])

# ============================================================
# 🧩 MODELOS Pydantic
# ============================================================
class SucursalBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    telefono: Optional[str] = None
    encargado: Optional[str] = None

class SucursalCreate(SucursalBase):
    pass

class SucursalResponse(SucursalBase):
    id: int
    fecha_creacion: datetime
    class Config:
        from_attributes = True

# ============================================================
# 📡 ENDPOINTS
# ============================================================

@router.get("/", response_model=List[SucursalResponse])
def listar_sucursales(db: Session = Depends(get_db)):
    return db.query(Sucursal).all()

@router.get("/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return sucursal

@router.post("/", response_model=SucursalResponse)
def crear_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
    existe = db.query(Sucursal).filter(Sucursal.nombre == sucursal.nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal con ese nombre")
    nueva = Sucursal(**sucursal.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@router.put("/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(sucursal_id: int, data: SucursalCreate, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    for key, value in data.dict().items():
        setattr(sucursal, key, value)
    db.commit()
    db.refresh(sucursal)
    return sucursal

@router.get("/{sucursal_id}/inventario")
def obtener_inventario_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    productos = db.query(Producto).filter(Producto.sucursal_id == sucursal_id).all()
    return {
        "sucursal": sucursal.nombre,
        "total_productos": len(productos),
        "inventario": productos
    }
