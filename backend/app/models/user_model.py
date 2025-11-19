# ============================================================
# 👤 MODELO DE USUARIO (Versión fusionada: antigua + mejorada)
# Compatible con MySQL actualizado, sucursales y roles nuevos
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import bcrypt

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    rol = Column(
        Enum("admin", "bodega", "sucursal", name="rol_usuario"),
        nullable=False,
        default="sucursal"
    )

    fecha_creacion = Column(DateTime, default=datetime.now)

    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)

    # Relación correcta hacia Sucursal
    sucursal = relationship(
        "app.models.sucursal_model.Sucursal",
        back_populates="usuarios",
        lazy="joined"
    )

    activo = Column(Boolean, default=True)

    actualizado_en = Column(DateTime, onupdate=datetime.now)

    @staticmethod
    def encriptar_password(password: str) -> str:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verificar_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
