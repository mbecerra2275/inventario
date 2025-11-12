from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base
import bcrypt

# ============================================================
# 👤 MODELO DE USUARIO
# ============================================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(50), default="Administrador")  # Roles: Administrador, contable, Bodeguero
    fecha_creacion = Column(DateTime, default=datetime.now)

    # ============================================================
    # 🧩 MÉTODOS AUXILIARES
    # ============================================================

    @staticmethod
    def encriptar_password(password: str) -> str:
        """Genera un hash seguro de la contraseña usando bcrypt."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña ingresada coincide con el hash almacenado."""
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))
