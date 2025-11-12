# ============================================================
# 🔐 Módulo de autenticación con JWT
# Autor: Milton Becerra Contreras
# ============================================================

from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
from fastapi import APIRouter, Header, HTTPException
import os

# ------------------------------------------------------------
# Cargar variables de entorno desde .env
# ------------------------------------------------------------
load_dotenv()

# Clave secreta y algoritmo
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

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
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

# ------------------------------------------------------------
# 🔍 Verificar token JWT
# ------------------------------------------------------------
def verificar_token(token: str):
    """
    Verifica y decodifica un token JWT. Retorna los datos del usuario si es válido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    Permite renovar el token JWT antes o después de expirar.
    Se debe enviar el token actual en el encabezado Authorization: Bearer <token>.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante")

    old_token = authorization.split(" ")[1]
    payload = verificar_token(old_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    # Elimina campos de control y genera nuevo token
    nuevo_token = crear_token(
        {k: v for k, v in payload.items() if k != "exp"},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": nuevo_token}

print("🔑 SECRET_KEY cargada:", SECRET_KEY)
