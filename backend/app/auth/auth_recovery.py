# ============================================================
# 📌 RECUPERACIÓN DE CONTRASEÑA (MODO DESARROLLO)
# El código se devuelve en la respuesta JSON (NO SE ENVÍA EMAIL)
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from app.database.connection import SessionLocal
from app.models.user_model import Usuario
from app.auth.auth import hash_password


router = APIRouter(prefix="/auth/recovery", tags=["Recuperación de contraseña"])


# ------------------------------ DB ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# 1️⃣ SOLICITAR CÓDIGO DE RECUPERACIÓN
# ============================================================
@router.post("/solicitar")
def solicitar_codigo(data: dict, db: Session = Depends(get_db)):

    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Debe ingresar un correo")

    usuario = db.query(Usuario).filter(Usuario.correo == email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    # 🔢 Generar código de 6 dígitos
    codigo = str(random.randint(100000, 999999))

    # Guardar código temporal
    usuario.codigo_recuperacion = codigo
    usuario.codigo_expira = datetime.utcnow() + timedelta(minutes=10)

    db.commit()

    return {
        "mensaje": "Código de recuperación generado",
        "codigo_debug": codigo   # 👈 MODO DESARROLLO
    }


# ============================================================
# 2️⃣ VALIDAR CÓDIGO
# ============================================================
@router.post("/validar")
def validar_codigo(data: dict, db: Session = Depends(get_db)):

    email = data.get("email")
    codigo = data.get("codigo")

    usuario = db.query(Usuario).filter(Usuario.correo == email).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no encontrado")

    if usuario.codigo_recuperacion != codigo:
        raise HTTPException(status_code=400, detail="Código incorrecto")

    if usuario.codigo_expira < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Código expirado")

    return {"mensaje": "Código validado correctamente"}


# ============================================================
# 3️⃣ RESTABLECER CONTRASEÑA
# ============================================================
@router.post("/restablecer")
def restablecer_password(data: dict, db: Session = Depends(get_db)):
    correo = data.get("correo")
    nueva = data.get("nueva_contrasena")

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(404, "El correo no existe")

    # Validar código
    if usuario.codigo_recuperacion != data.get("codigo"):
        raise HTTPException(400, "Código incorrecto")

    if usuario.codigo_expira < datetime.now():
        raise HTTPException(400, "Código expirado")

    usuario.password_hash = Usuario.encriptar_password(nueva)

    usuario.codigo_recuperacion = None
    usuario.codigo_expira = None

    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}
