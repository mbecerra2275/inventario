# ============================================================
# Dashboard Router FINAL
# ============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.database.connection import SessionLocal
from app.models.producto_model import Producto
from app.models.sucursal_model import Sucursal

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/metricas")
def metricas_dashboard(db: Session = Depends(get_db)):
    stock_bajo = db.query(Producto).filter(Producto.cantidad <= 5).count()
    total_productos = db.query(Producto).count()

    hace_30 = datetime.now() - timedelta(days=30)
    productos_nuevos = db.query(Producto).filter(
        Producto.fecha_creacion >= hace_30
    ).count()

    sucursales_activas = db.query(Sucursal).filter(Sucursal.estado == "Activo").count()

    return {
        "stock_bajo": stock_bajo,
        "sucursales_activas": sucursales_activas,
        "total_productos": total_productos,
        "productos_nuevos": productos_nuevos
    }


@router.get("/sucursales/activas")
def sucursales_activas(db: Session = Depends(get_db)):
    return db.query(Sucursal).filter(Sucursal.estado == "Activo").all()


@router.get("/categorias/distribucion")
def categorias(db: Session = Depends(get_db)):
    rows = (
        db.query(Producto.clasificacion, func.count(Producto.id))
        .group_by(Producto.clasificacion)
        .all()
    )

    return [{"categoria": c if c else "Sin clasificación", "total": t} for c, t in rows]
