from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.producto_model import Producto

router = APIRouter(prefix="/productos", tags=["Productos"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------
# /productos/schema -> columnas para el formulario dinámico
# ------------------------------------------------------------
@router.get("/schema")
def obtener_schema(db: Session = Depends(get_db)):
    columnas = []
    for col in Producto.__table__.columns:
        columnas.append({
            "name": col.name,
            "type": str(col.type)
        })
    return columnas


# ------------------------------------------------------------
# /productos -> lista completa (para tabla y edición)
# ------------------------------------------------------------
@router.get("/")
def obtener_productos(db: Session = Depends(get_db)):
    return db.query(Producto).all()


# ------------------------------------------------------------
# /productos/recientes -> últimos N productos
# ------------------------------------------------------------
@router.get("/recientes")
def productos_recientes(limit: int = 5, db: Session = Depends(get_db)):
    return (
        db.query(Producto)
        .order_by(Producto.fecha_creacion.desc())
        .limit(limit)
        .all()
    )
