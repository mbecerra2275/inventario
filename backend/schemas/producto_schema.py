from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductoBase(BaseModel):
    nombre: Optional[str] = None
    clasificacion: Optional[str] = None
    tipo_producto: Optional[str] = None
    estado: Optional[str] = None
    impuestos: Optional[float] = None
    codigo_sku: Optional[str] = None
    marca: Optional[str] = None
    precio: Optional[float] = None
    cantidad: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    sucursal_id: Optional[int] = None
    costo_neto_unitario: Optional[float] = None  # ✅ cambio aquí
    costo_neto_total: Optional[float] = None     # ✅ y aquí

class ProductoCreate(ProductoBase):
    pass

class ProductoOut(ProductoBase):
    id: int

    class Config:
        orm_mode = True
