"""
==========================================
 Módulo: auth.py
 Autor: Milton Becerra
 Descripción:
 Manejo de autenticación, generación y verificación
 de tokens JWT para todo el sistema.
==========================================
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# ============================================================
# 🔒 CONFIGURACIÓN BÁSICA DEL TOKEN
# ============================================================
SECRET_KEY = "TuClaveSuperSecreta123"  # ⚠️ reemplázala por una real en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # duración del token

# Contexto de encriptación (para contraseñas)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer → busca automáticamente el token en el header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/login")

# ============================================================
# 🔑 FUNCIONES PARA HASH Y VERIFICACIÓN DE CONTRASEÑAS
# ============================================================

def hash_password(password: str) -> str:
    """Cifra la contraseña con bcrypt"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verifica si la contraseña ingresada coincide con la almacenada"""
    return pwd_context.verify(password, hashed)

# ============================================================
# 🧾 GENERAR TOKEN JWT
# ============================================================

def crear_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un token JWT a partir de los datos del usuario.
    Incluye fecha de expiración.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    token_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token_jwt

# ============================================================
# 🔍 VERIFICAR TOKEN JWT (Dependencia global)
# ============================================================

def verificar_token(token: str = Depends(oauth2_scheme)):
    """
    Verifica el token recibido desde el encabezado Authorization.
    Retorna los datos decodificados del usuario.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # ej: {"sub": correo, "rol": "Admin", "nombre": "Milton"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ============================================================
# 🔒 VALIDACIÓN DE ROLES (OPCIONAL)
# ============================================================

def require_admin(usuario: dict = Depends(verificar_token)):
    """Permite acceso solo a usuarios con rol Admin"""
    if usuario.get("rol") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción",
        )
    return usuario

def require_gestor(usuario: dict = Depends(verificar_token)):
    """Permite acceso a Admin o Gestor"""
    if usuario.get("rol") not in ["Admin", "Gestor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo Gestores o Administradores pueden realizar esta acción",
        )
    return usuario
