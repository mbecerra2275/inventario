from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, productos, sucursales, informes, verificacion
from app.database.connection import init_db  # 👈 mantiene la lógica original
from app.auth.auth import router as auth_router

# ============================================================
# 🚀 Configuración base de la aplicación
# ============================================================
app = FastAPI(title="App de Inventario", version="2.0.1")
app.router.redirect_slashes = False

# ============================================================
# 🌐 Configuración global CORS (válida para todos los endpoints)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# ============================================================
# ⚙️ Evento de inicio: inicialización de la base de datos
# ============================================================
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Base de datos inicializada")
    print("✅ CORS habilitado")

# ============================================================
# 🔗 Inclusión de routers (rutas de la API)
# ============================================================
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(sucursales.router)
app.include_router(verificacion.router)
app.include_router(informes.router)
app.include_router(auth_router)

# ============================================================
# 🏁 Endpoint raíz
# ============================================================
@app.get("/")
def root():
    return {"mensaje": "API de Inventario funcionando", "version": "2.0.1"}

# ============================================================
# 🧩 Ejecución directa (solo en desarrollo)
# ============================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
