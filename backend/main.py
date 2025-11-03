
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import usuarios, productos, sucursales
from backend.database import init_db


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
    allow_methods=["GET","POST","PUT","DELETE","OPTIONS"],
    allow_headers=["*"],
)
#===============================
# Evento Starup 
#===============================
@app.on_event("startup")
def startup():
    init_db()
    print("✅ Base de datos inicializada")
    print("✅ CORS habilitado")

# Incluir routers
app.include_router(usuarios.router)
app.include_router(productos.router)
app.include_router(sucursales.router)

@app.get("/")
def root():
    return {"mensaje": "API de Inventario funcionando", "version": "1.0.1"}
