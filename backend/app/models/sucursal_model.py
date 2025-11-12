from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Sucursal(Base):
    """Tabla de sucursales (sincronizada con MySQL)"""
    __tablename__ = "sucursales"
    __table_args__ = {"extend_existing": True}  # Evita conflicto si ya está registrada

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    estado = Column(String(20), default="Activo")
    encargado = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.now)
