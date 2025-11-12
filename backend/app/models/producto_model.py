from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from app.database.connection import Base

# ============================================================
# 🧱 Modelo alineado con la tabla 'productos' existente en MySQL
# ============================================================
class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    clasificacion = Column(String(100))
    tipo_producto = Column(String(100))
    estado = Column(String(50))
    impuestos = Column(Float)
    codigo_sku = Column(String(50))
    marca = Column(String(100))
    precio = Column(Float)
    cantidad = Column(Integer)
    fecha_creacion = Column(DateTime)
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"))
    costo_neto_unitario = Column(Float)
    costo_neto_total = Column(Float)
    doc_recepcion_ing = Column(String(50))
