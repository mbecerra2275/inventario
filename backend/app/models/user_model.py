# ============================================================
# 👤 MODELO DE USUARIO — Versión completa y corregida
# Incluye: roles, relación con sucursales, recuperación de contraseña
# ============================================================

from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey,
    Boolean, Enum
)
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import bcrypt

from app.database.connection import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    # ------------------------------------------------------------
    # 🧩 CAMPOS PRINCIPALES DEL USUARIO
    # ------------------------------------------------------------
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

    # ------------------------------------------------------------
    # 🏪 RELACIÓN CON SUCURSAL
    # ------------------------------------------------------------
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)

    sucursal = relationship(
        "app.models.sucursal_model.Sucursal",
        back_populates="usuarios",
        lazy="joined"
    )

    activo = Column(Boolean, default=True)
    actualizado_en = Column(DateTime, onupdate=datetime.now)

    # ------------------------------------------------------------
    # 🔐 CAMPOS NUEVOS PARA RECUPERACIÓN DE CONTRASEÑA
    # ------------------------------------------------------------
    codigo_recuperacion = Column(String(6), nullable=True)
    codigo_expira = Column(DateTime, nullable=True)

    # ------------------------------------------------------------
    # 🔑 MÉTODOS DE AUTENTICACIÓN
    # ------------------------------------------------------------
    @staticmethod
    def encriptar_password(password: str) -> str:
        """Genera un hash seguro para la contraseña."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
