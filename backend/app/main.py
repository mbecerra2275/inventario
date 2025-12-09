from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import usuarios, productos, sucursales, informes, verificacion
from app.database.connection import init_db  # 👈 mantiene la lógica original
from app.auth.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router
from app.routers import logs
from app.auth.auth_recovery import router as recovery_router
from fastapi.openapi.docs import get_redoc_html

# ============================================================
# 🚀 Configuración base de la aplicación
# ============================================================
app = FastAPI(
    title="Sistema de Inventario",
    description="Documentación de API",
    version="1.4.0",
    docs_url="/docs",
    redoc_url=None  # desactiva redoc por defecto
)
# ============================================================
# 🌐 Configuración global CORS (válida para todos los endpoints)
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",

    ],  # Permitir todas las fuentes (orígenes)
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

@app.get("/redoc", include_in_schema=False)
async def redoc_ui():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="ReDoc",
        redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"
    )    

# ============================================================
# 🔗 Inclusión de routers (rutas de la API)
# ============================================================
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(sucursales.router)
app.include_router(verificacion.router)
app.include_router(informes.router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(logs.router)
app.include_router(recovery_router)

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
