from fastapi import APIRouter, HTTPException
from backend.auth import verificar_token  # usa tu auth original

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.get("/verificar")
def validar_token(token: str):
    """
    Verifica si el token JWT recibido es válido.
    """
    datos = verificar_token(token)
    if not datos:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    return {
        "valido": True,
        "usuario": datos.get("sub"),
        "rol": datos.get("rol"),
        "nombre": datos.get("nombre")
    }
