from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models.sucursal_model import Sucursal
from app.schemas.sucursal_schema import SucursalCreate, SucursalOut

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- LISTAR ----------
@router.get("/", response_model=List[SucursalOut])
def listar_sucursales(db: Session = Depends(get_db)):
    return db.query(Sucursal).all()


# ---------- CREAR ----------
@router.post("/", response_model=SucursalOut)
def crear_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
    nueva = Sucursal(**sucursal.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# ---------- ACTUALIZAR ----------
@router.put("/{sucursal_id}", response_model=SucursalOut)
def actualizar_sucursal(sucursal_id: int, datos: SucursalCreate, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(sucursal, campo, valor)

    db.commit()
    db.refresh(sucursal)
    return sucursal


# ---------- ELIMINAR ----------
@router.delete("/{sucursal_id}")
def eliminar_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    db.delete(sucursal)
    db.commit()
    return {"mensaje": "Sucursal eliminada correctamente"}
