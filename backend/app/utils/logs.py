from fastapi import Request
from sqlalchemy.orm import Session
from app.models.log_model import LogConexion

def registrar_log(db: Session, usuario_id: int, evento: str, request: Request, detalle: str = None):
    ip = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None

    log = LogConexion(
        usuario_id=usuario_id,
        evento=evento,
        ip=ip,
        user_agent=user_agent,
        detalle=detalle
    )

    db.add(log)
    db.commit()
