# ============================================================
# 🔐 MÓDULO: reset_password.py
# Gestión de recuperación y cambio de contraseñas
# Autor: Milton Becerra
# ============================================================

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random, string
from passlib.context import CryptContext

from app.database.connection import SessionLocal
from app.models.user_model import Usuario
from app.auth.auth import crear_token, verificar_token, rol_requerido

# -----------------------------
# 🔧 Configuración inicial
# -----------------------------
router = APIRouter(prefix="/auth", tags=["Autenticación"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -----------------------------
# 🔌 Conexión a la BD
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------
# 🧩 Generar código temporal
# -----------------------------
def generar_codigo():
    return ''.join(random.choices(string.digits, k=6))


# ============================================================
# 📤 SOLICITAR RECUPERACIÓN DE CONTRASEÑA
# ============================================================
@router.post("/recuperar")
def solicitar_codigo(data: dict, db: Session = Depends(get_db)):
    """
    Solicita un código de verificación para recuperar la contraseña.
    """
    email = data.get("email")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    # Generar código
    codigo = generar_codigo()
    usuario.codigo_reset = codigo
    usuario.codigo_reset_expira = datetime.now() + timedelta(minutes=10)

    db.commit()

    # Aquí deberías enviar correo → por ahora lo devolvemos para pruebas
    return {
        "mensaje": "Código de recuperación generado",
        "codigo_debug": codigo  # ❗ En producción se elimina
    }


# ============================================================
# 🔐 VALIDAR CÓDIGO DE RECUPERACIÓN
# ============================================================
@router.post("/validar-codigo")
def validar_codigo(data: dict, db: Session = Depends(get_db)):
    """
    Valida el código enviado por correo.
    """
    email = data.get("email")
    codigo = data.get("codigo")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    if usuario.codigo_reset != codigo:
        raise HTTPException(status_code=400, detail="Código incorrecto")

    if usuario.codigo_reset_expira < datetime.now():
        raise HTTPException(status_code=400, detail="Código expirado")

    return {"mensaje": "Código válido"}


# ============================================================
# 🔄 CAMBIAR CONTRASEÑA (DESPUÉS DE VALIDAR CÓDIGO)
# ============================================================
@router.post("/restablecer")
def restablecer_password(data: dict, db: Session = Depends(get_db)):
    """
    Cambia la contraseña después de validar el código.
    """
    email = data.get("email")
    nueva = data.get("password")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    usuario.password = pwd_context.hash(nueva)
    usuario.codigo_reset = None
    usuario.codigo_reset_expira = None

    db.commit()

    return {"mensaje": "Contraseña actualizada correctamente"}


# ============================================================
# 🟦 CAMBIAR CONTRASEÑA (USUARIO AUTENTICADO)
# ============================================================
@router.put(
    "/cambiar-password",
    dependencies=[Depends(rol_requerido(["admin", "bodega", "sucursal"]))]
)
def cambiar_password(data: dict, token_data = Depends(verificar_token), db: Session = Depends(get_db)):
    """
    Cambia la contraseña desde el usuario autenticado.
    """
    usuario_id = token_data["id"]
    nueva = data.get("password")

    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.password = pwd_context.hash(nueva)
    db.commit()

    return {"mensaje": "Contraseña cambiada correctamente"}
