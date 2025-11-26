# ============================================================
#  ROUTER DE USUARIOS - LOGIN / REGISTRO / PERFILES
#  Corregido para compatibilidad total con JWT + roles
# ============================================================

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, Form, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.database.connection import get_db
from app.models.user_model import Usuario
from fastapi import Request, BackgroundTasks
from app.utils.logs import registrar_log
from app.auth.auth import crear_token, verificar_token

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


# =========================
# JWT / Seguridad
# =========================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/token")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)):
    """
    Lee y valida el JWT. Devuelve un dict con {id, correo, rol, nombre}
    """
    try:
        payload = verificar_token(token)

        # 🔥 Normalizar el rol SIEMPRE
        if "rol" in payload:
            payload["rol"] = payload["rol"].lower()

        return payload
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def require_admin(usuario_actual: dict = Depends(obtener_usuario_actual)):
    """
    Solo permite acceso a ADMIN (rol = 'admin')
    """
    if usuario_actual.get("rol") != "admin":   # 🔥 antes comparaba 'Admin', incorrecto
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Administradores pueden realizar esta acción"
        )
    return usuario_actual


# =========================
# Modelos Pydantic
# =========================
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    rol: Optional[str] = Field(None, description="admin | bodega | sucursal")


class CambiarPassword(BaseModel):
    password_actual: str = Field(min_length=6)
    password_nueva: str = Field(min_length=6)


class ResetPasswordAdmin(BaseModel):
    correo: EmailStr
    password_nueva: str = Field(min_length=6)


# =========================
# Registro
# =========================
@router.post("/registro")
def registrar_usuario(
    nombre: str = Form(...),
    correo: str = Form(...),
    password: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_db)
):
    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed = Usuario.encriptar_password(password)
    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        password_hash=hashed,
        rol=rol.lower()   # 🔥 normalizar rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario creado correctamente",
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }


# =========================
# Token OAuth2 (para Swagger)
# =========================
@router.post("/token")
def oauth2_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    correo = form_data.username
    password = form_data.password

    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()
    if not usuario or not usuario.verificar_password(password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = crear_token({
        "id": usuario.id,
        "sub": usuario.correo,
        "rol": usuario.rol.lower(),      # 🔥 normalizar rol
        "nombre": usuario.nombre
    })

    return {"access_token": token, "token_type": "bearer"}


# =========================
# Login desde frontend
# =========================
@router.post("/login")
def login_usuario(
    request: Request,
    background_tasks: BackgroundTasks,
    correo: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    # -------- LOGIN FALLIDO --------
    if not usuario or not usuario.verificar_password(password):
        background_tasks.add_task(
            registrar_log,
            db=db,
            usuario_id=None,
            evento="login_fallido",
            request=request,
            detalle=f"correo={correo}"
        )
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # -------- LOGIN EXITOSO --------
    token = crear_token({
        "id": usuario.id,
        "sub": usuario.correo,
        "rol": usuario.rol,
        "nombre": usuario.nombre
    })

    background_tasks.add_task(
        registrar_log,
        db=db,
        usuario_id=usuario.id,
        evento="login_exitoso",
        request=request,
        detalle=None
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "nombre": usuario.nombre
    }


# =========================
# Editar usuario
# =========================
@router.put("/{usuario_id}")
def editar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    u: Usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    es_admin = (usuario_actual.get("rol") == "admin")
    es_propio = (usuario_actual.get("id") == usuario_id)

    # Validación de permisos
    if not (es_admin or es_propio):
        raise HTTPException(status_code=403, detail="No autorizado")

    if data.rol is not None and not es_admin:
        raise HTTPException(status_code=403, detail="Solo Admin puede cambiar el rol")

    # Validar correo duplicado
    if data.correo and data.correo != u.correo:
        existe = db.query(Usuario).filter(Usuario.correo == data.correo).first()
        if existe:
            raise HTTPException(status_code=400, detail="El correo ya está usado")

    # Aplicar cambios
    if data.nombre is not None:
        u.nombre = data.nombre
    if data.correo is not None:
        u.correo = data.correo
    if es_admin and data.rol is not None:
        u.rol = data.rol.lower()   # 🔥 normalizar rol

    db.commit()
    db.refresh(u)
    return {
        "id": u.id,
        "nombre": u.nombre,
        "correo": u.correo,
        "rol": u.rol,
        "mensaje": "Usuario actualizado correctamente"
    }


# =========================
# Cambiar password (propio)
# =========================
@router.post("/cambiar-password")
def cambiar_password(
    payload: CambiarPassword,
    db: Session = Depends(get_db),
    usuario_actual: dict = Depends(obtener_usuario_actual)
):
    u: Usuario = db.query(Usuario).filter(Usuario.id == usuario_actual["id"]).first()
    if not u:
        raise HTTPException(statuscode=404, detail="Usuario no encontrado")

    if not u.verificar_password(payload.password_actual):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")

    u.password_hash = Usuario.encriptar_password(payload.password_nueva)
    db.commit()
    return {"mensaje": "Contraseña actualizada correctamente"}


# =========================
# Reset password (Admin)
# =========================
@router.post("/reset-password")
def reset_password_admin(
    payload: ResetPasswordAdmin,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin)
):
    u: Usuario = db.query(Usuario).filter(Usuario.correo == payload.correo).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    u.password_hash = Usuario.encriptar_password(payload.password_nueva)
    db.commit()
    return {"mensaje": f"Contraseña restablecida para {payload.correo}"}

