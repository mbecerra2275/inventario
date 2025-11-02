"""
==========================================
 Módulo: database.py
 Autor: Milton Becerra
 Descripción:
 Configura la conexión MySQL, define los modelos
 de datos (Producto y Sucursal) y provee funciones
 de inicialización y sesión de base de datos.
==========================================
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# ============================================================
# 🔹 Cargar variables de entorno desde .env
# ============================================================
load_dotenv()

DB_USER = os.getenv("DB_USER", "inventario_user")
DB_PASS = os.getenv("DB_PASS", "TuClaveSegura")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inventario")

# ============================================================
# 🔹 Configuración de conexión MySQL (usando PyMySQL)
# ============================================================
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,           # Cambia a True para ver las consultas SQL en consola
    pool_pre_ping=True    # Verifica conexión antes de cada consulta
)

# ============================================================
# 🔹 Configuración de sesión de SQLAlchemy
# ============================================================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# 🧱 MODELOS DE BASE DE DATOS
# ============================================================

class Sucursal(Base):
    """Tabla de sucursales (filiales, bodegas, tiendas, etc.)"""
    __tablename__ = "sucursales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    direccion = Column(String(200), nullable=True)
    ciudad = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    encargado = Column(String(100), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Si luego deseas reactivar la relación con Producto:
    #productos = relationship("Producto", backref="sucursal", lazy="joined")


class Producto(Base):
    """Tabla de productos del inventario"""
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

    # Relación con sucursal
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=True)


# ============================================================
# ⚙️ FUNCIONES DE INICIALIZACIÓN Y SESIÓN
# ============================================================
def init_db():
    """
    Crea las tablas en la base de datos si no existen.
    Ejecutar una vez al iniciar la aplicación.
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas/verificadas en MySQL.")


def get_db():
    """
    Generador que devuelve una sesión activa de base de datos.
    Se asegura de cerrarla correctamente al finalizar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 🧩 TEST OPCIONAL: Verificar conexión manualmente
# ============================================================
if __name__ == "__main__":
    try:
        print("🔍 Verificando conexión con la base de datos...")
        with engine.connect() as connection:
            result = connection.execute("SELECT NOW();")
            print(f"✅ Conectado correctamente. Hora del servidor: {list(result)[0][0]}")
        init_db()
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
