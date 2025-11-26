from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from app.database import Base

class LogConexion(Base):
    __tablename__ = "logs_conexiones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    evento = Column(String(100), nullable=False)
    ip = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    detalle = Column(Text, nullable=True)
    fecha = Column(DateTime, default=datetime.now)
