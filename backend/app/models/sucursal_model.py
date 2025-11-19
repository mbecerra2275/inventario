from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Sucursal(Base):
    __tablename__ = "sucursales"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)

    estado = Column(String(20), default="Activo")
    encargado = Column(String(100), nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.now)

    # Relación inversa
    usuarios = relationship(
        "app.models.user_model.Usuario",
        back_populates="sucursal"
    )
