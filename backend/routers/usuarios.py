from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user_model import Usuario
from backend.auth import crear_token

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

# ============================================================
# 🧩 REGISTRO DE NUEVO USUARIO
# ============================================================
@router.post("/registro")
def registrar_usuario(
    nombre: str = Form(...),
    correo: str = Form(...),
    password: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo usuario con contraseña encriptada.
    """
    existente = db.query(Usuario).filter(Usuario.correo == correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed = Usuario.encriptar_password(password)
    nuevo_usuario = Usuario(
        nombre=nombre,
        correo=correo,
        password_hash=hashed,
        rol=rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario creado correctamente",
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }

# ============================================================
# 🔐 LOGIN DE USUARIO
# ============================================================
@router.post("/login")
def login(
    correo: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Valida las credenciales del usuario y genera un token JWT si son correctas.
    """
    usuario = db.query(Usuario).filter(Usuario.correo == correo).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    if not usuario.verificar_password(password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token({
        "sub": usuario.correo,
        "rol": usuario.rol,
        "nombre": usuario.nombre
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.rol,
        "nombre": usuario.nombre
    }

# ============================================================
# 👥 OBTENER LISTA DE USUARIOS (solo para pruebas)
# ============================================================
@router.get("/listar")
def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [
        {"id": u.id, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}
        for u in usuarios
    ]
