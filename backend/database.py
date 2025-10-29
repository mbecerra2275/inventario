from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey
from datetime import datetime
import os
from dotenv import load_dotenv

# ============================================================
# Carga de variables de entorno desde .env (seguridad y portabilidad)
# ============================================================
load_dotenv()

DB_USER = os.getenv("DB_USER", "inventario_user")
DB_PASS = os.getenv("DB_PASS", "TuClaveSegura")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inventario")

# ============================================================
# Configuración de conexión MySQL (usa PyMySQL como driver)
# ============================================================
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# Modelo de Producto (igual al tuyo, con soporte a MySQL)
# ============================================================
class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    clasificacion = Column(String(100), nullable=True)
    tipo_producto = Column(String(100), nullable=True)
    estado = Column(String(50), default="Activo")
    impuestos = Column(Float, default=19.0)  # IVA por defecto 19%
    codigo_sku = Column(String(50), unique=True, nullable=True)
    marca = Column(String(100), nullable=True)
    precio = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)

 # 🔹 NUEVO: vincular producto a sucursal
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)   

# ============================================================
# Inicialización y sesión de base de datos
# ============================================================
def init_db():
    """Crea las tablas si no existen"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas en MySQL.")

def get_db():
    """Genera una sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

# ============================================================
# NUEVA TABLA: Sucursal
# ============================================================

class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    encargado = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # ❌ Desactivar la relación hasta agregar sucursal_id en Producto
    # productos = relationship("Producto", backref="sucursal", lazy="joined")
