# ============================================================
# 🔐 Módulo de autenticación con JWT
# Autor: Milton Becerra Contreras
# ============================================================

from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException, Depends, status

import os

# ------------------------------------------------------------
# Cargar variables de entorno desde .env
# ------------------------------------------------------------
load_dotenv()

# Clave secreta y algoritmo
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Validar que la clave exista al iniciar
if not SECRET_KEY or SECRET_KEY.strip() == "":
    raise ValueError("❌ ERROR: SECRET_KEY no está definida en el archivo .env")

# ------------------------------------------------------------
# 🧾 Crear token JWT
# ------------------------------------------------------------
def crear_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """
    Crea un token JWT con la información del usuario.
    """
    to_encode = data.copy()

    # Normalizar rol siempre
    if "rol" in to_encode:
        to_encode["rol"] = to_encode["rol"].lower()

    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# ------------------------------------------------------------
# 🔍 Verificar token JWT (solo decodifica)
# ------------------------------------------------------------
def verificar_token(token: str):
    """
    Verifica y decodifica un token JWT. Retorna los datos si es válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Normalizar rol
        if "rol" in payload:
            payload["rol"] = payload["rol"].lower()

        return payload

    except JWTError as e:
        print("❌ Token inválido:", e)
        return None


# ------------------------------------------------------------
# 🔄 Endpoint para refrescar token
# ------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.get("/refresh")
def refresh_token(authorization: str = Header(None)):
    """
    Permite renovar el token JWT enviando:
        Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante")

    old_token = authorization.split(" ")[1]
    payload = verificar_token(old_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    nuevo_token = crear_token(
        {k: v for k, v in payload.items() if k != "exp"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": nuevo_token}


# ============================================================
# 🛡️ Obtener datos del token (usuario + rol)
# ============================================================
def obtener_usuario_token(authorization: str = Header(None)):
    """
    Lee token desde:
        Authorization: Bearer <token>
    y retorna {usuario_id, rol, nombre}
    """

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token faltante"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Esquema inválido")
    except:
        raise HTTPException(
            status_code=401,
            detail="Formato de Authorization inválido (use: Bearer <token>)"
        )

    # Decodificar token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        usuario_id = payload.get("id") or payload.get("sub")
        rol = payload.get("rol")
        nombre = payload.get("nombre")

        # Valores obligatorios
        if usuario_id is None or rol is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Normalizar rol a minúsculas SIEMPRE
        rol = rol.lower()

        return {
            "usuario_id": usuario_id,
            "rol": rol,
            "nombre": nombre
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )


# ============================================================
# 🛡️ Dependencia de roles
# ============================================================
def rol_requerido(roles_permitidos: list):
    """
    Ejemplo:
       @router.get("/", dependencies=[Depends(rol_requerido(["admin", "bodega"]))])
    """
    # Normalizar roles permitidos
    roles_permitidos = [r.lower() for r in roles_permitidos]

    def verificar_acceso(usuario = Depends(obtener_usuario_token)):
        rol_usuario = usuario.get("rol")

        if rol_usuario not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Rol '{rol_usuario}' no permitido (se requiere uno de: {roles_permitidos})"
            )
        return usuario

    return verificar_acceso


# Debug: mostrar clave cargada
print("🔑 SECRET_KEY cargada:", SECRET_KEY)

