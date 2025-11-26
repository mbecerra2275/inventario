from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.log_model import LogConexion
from app.auth.auth import rol_requerido

router = APIRouter(prefix="/logs", tags=["Logs"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="usuarios/token")


# ---------- DEPENDENCIA DB ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- LISTAR LOGS ----------
@router.get("/")
def obtener_logs(
    limit: int = 200,
    token: str = Depends(oauth2_scheme),
    usuario_actual: dict = Depends(rol_requerido(["admin"])),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(LogConexion)
        .order_by(LogConexion.fecha.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": log.id,
            "usuario_id": log.usuario_id,
            "evento": log.evento,
            "ip": log.ip,
            "user_agent": log.user_agent,
            "detalle": log.detalle,
            "fecha": log.fecha,
        }
        for log in logs
    ]
