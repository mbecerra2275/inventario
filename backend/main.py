
"""
==========================================
 Módulo: main.py
 Autor: Milton Becerra
 Descripción:
 Backend principal del Sistema de Gestión de Inventario.
 - Configura CORS
 - Inicializa la base de datos
 - Define endpoints globales
 - Conecta routers: Usuarios, Productos, Sucursales
==========================================
"""

# ============================================================
# 🔹 Importaciones base
# ============================================================
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ============================================================
# 🔹 Base de datos y modelos
# ============================================================
from backend.database import get_db, init_db, Producto, Sucursal
from backend.routers import usuarios, productos, sucursales
from backend.auth import verificar_token

# ============================================================
# 🚀 Inicializar aplicación FastAPI
# ============================================================
app = FastAPI(
    title="Sistema de Gestión de Inventario",
    version="1.0.1",
    description="API central para gestión de usuarios, productos y sucursales"
)

# ============================================================
# 🔐 CORS (Cross-Origin Resource Sharing)
# ============================================================
origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5500",
    "http://localhost",
    "http://localhost:5500",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🔧 INICIALIZACIÓN DE BASE DE DATOS
# ============================================================
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Base de datos inicializada correctamente.")
    print("✅ CORS habilitado para frontend local.")

# ============================================================
# 🔑 AUTENTICACIÓN Y PERMISOS POR ROL
# ============================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    return verificar_token(token)

def permiso_admin(usuario: dict = Depends(obtener_usuario_actual)):
    if usuario.get("rol") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a administradores")
    return usuario

def permiso_gestor(usuario: dict = Depends(obtener_usuario_actual)):
    if usuario.get("rol") not in ["Admin", "Gestor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo Gestores o Administradores pueden realizar esta acción")
    return usuario

# ============================================================
# 📦 MODELOS Pydantic
# ============================================================

# --- PRODUCTOS ---
class ProductoCreate(BaseModel):
    nombre: str
    clasificacion: Optional[str] = None
    tipo_producto: Optional[str] = None
    estado: str = "Activo"
    impuestos: float = 19.0
    codigo_sku: Optional[str] = None
    marca: Optional[str] = None
    precio: float
    cantidad: int
    sucursal_id: Optional[int] = None

class ProductoResponse(ProductoCreate):
    id: int
    fecha_creacion: datetime
    class Config:
        from_attributes = True

# --- SUCURSALES ---
class SucursalBase(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    telefono: Optional[str] = None
    encargado: Optional[str] = None

class SucursalCreate(SucursalBase):
    pass

class SucursalResponse(SucursalBase):
    id: int
    fecha_creacion: datetime
    class Config:
        from_attributes = True

# ============================================================
# 🌐 ENDPOINTS GLOBALES
# ============================================================
@app.get("/")
def root():
    return {
        "mensaje": "🚀 API del Sistema de Inventario funcionando correctamente",
        "version": "1.0.1",
        "cors": "habilitado"
    }

# ============================================================
# 🧩 PRODUCTOS
# ============================================================
@app.get("/productos", response_model=List[ProductoResponse])
def obtener_productos(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    productos = db.query(Producto).offset(skip).limit(limit).all()
    return productos

@app.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.post("/productos", response_model=ProductoResponse)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    if producto.codigo_sku:
        existe = db.query(Producto).filter(Producto.codigo_sku == producto.codigo_sku).first()
        if existe:
            raise HTTPException(status_code=400, detail="Ya existe un producto con ese código SKU")
    nuevo = Producto(**producto.dict())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, producto: ProductoCreate, db: Session = Depends(get_db)):
    producto_db = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for attr, value in producto.dict().items():
        setattr(producto_db, attr, value)

    db.commit()
    db.refresh(producto_db)
    return producto_db

@app.delete("/productos/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}

# ============================================================
# 🏢 SUCURSALES
# ============================================================
@app.get("/api/sucursales", response_model=List[SucursalResponse])
def listar_sucursales(db: Session = Depends(get_db)):
    return db.query(Sucursal).all()

@app.get("/api/sucursales/{sucursal_id}", response_model=SucursalResponse)
def obtener_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return sucursal

@app.post("/api/sucursales", response_model=SucursalResponse)
def crear_sucursal(sucursal: SucursalCreate, db: Session = Depends(get_db)):
    existe = db.query(Sucursal).filter(Sucursal.nombre == sucursal.nombre).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal con ese nombre")
    nueva = Sucursal(**sucursal.dict())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

@app.put("/api/sucursales/{sucursal_id}", response_model=SucursalResponse)
def actualizar_sucursal(sucursal_id: int, data: SucursalCreate, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    for key, value in data.dict().items():
        setattr(sucursal, key, value)
    db.commit()
    db.refresh(sucursal)
    return sucursal

@app.get("/api/sucursales/{sucursal_id}/inventario")
def obtener_inventario_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    productos = db.query(Producto).filter(Producto.sucursal_id == sucursal_id).all()
    return {
        "sucursal": sucursal.nombre,
        "total_productos": len(productos),
        "inventario": productos
    }

# ============================================================
# 🔗 INCLUIR ROUTER DE USUARIOS
# ============================================================
app.include_router(usuarios.router)
app.include_router(productos.router)  # ya tiene su prefijo "/productos"
app.include_router(sucursales.router) # ya tiene su prefijo "/api/sucursales"

# ============================================================
# 🧩 EJECUCIÓN LOCAL
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
