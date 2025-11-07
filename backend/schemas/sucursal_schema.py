from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SucursalBase(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    telefono: Optional[str] = None
    estado: Optional[str] = "Activo"
    encargado: Optional[str] = None

class SucursalCreate(SucursalBase):
    pass

class SucursalOut(SucursalBase):
    id: int
    fecha_creacion: Optional[datetime]

    class Config:
        orm_mode = True
