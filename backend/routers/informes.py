"""
==========================================
 Módulo: informes.py
 Autor: Milton Becerra
 Descripción:
 Rutas para exportar e importar datos del inventario.
 Permite:
   - Exportar productos en formato CSV o TXT.
   - Importar productos desde un archivo CSV.
 Requiere autenticación JWT.
==========================================
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv, io
from backend.database import get_db, Producto
from backend.auth import verificar_token
from typing import List

# Crear el router
router = APIRouter(
    prefix="/informes",
    tags=["Informes"]
)

# ============================================================
# 📤 EXPORTAR PRODUCTOS A CSV
# ============================================================

@router.get("/exportar/csv", response_description="Descargar CSV de productos")
def exportar_csv(
    db: Session = Depends(get_db),
    _: dict = Depends(verificar_token)  # Requiere token válido
):
    """
    Exporta todos los productos registrados en la base de datos a un archivo CSV.
    Solo accesible para usuarios autenticados.
    """
    productos = db.query(Producto).all()
    if not productos:
        raise HTTPException(status_code=404, detail="No hay productos registrados")

    # Crear buffer temporal para el archivo
    output = io.StringIO()
    writer = csv.writer(output)

    # Escribir encabezados (columnas)
    writer.writerow([
        "ID", "Nombre", "Clasificación", "Tipo", "Estado", "Impuestos",
        "Código SKU", "Marca", "Precio", "Cantidad", "Sucursal_ID", "Fecha Creación"
    ])

    # Escribir filas con los datos
    for p in productos:
        fecha = p.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if p.fecha_creacion else "sin fecha" 
        writer.writerow([
            p.id,
            p.nombre, 
            p.clasificacion, 
            p.tipo_producto, 
            p.estado,
            p.impuestos, 
            p.codigo_sku, 
            p.marca, 
            p.precio, 
            p.cantidad,
            p.sucursal_id, 
        
        ])

    output.seek(0)

    # Enviar como respuesta descargable
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=productos.csv"}
    )

# ============================================================
# 📥 IMPORTAR PRODUCTOS DESDE CSV
# ============================================================

@router.post("/importar/csv", response_description="Subir CSV de productos")
def importar_csv(
    archivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: dict = Depends(verificar_token)
):
    """
    Permite cargar productos desde un archivo CSV.
    El CSV debe contener las columnas en el mismo orden del exportado.
    """
    # Validar tipo de archivo
    if not archivo.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Debe subir un archivo CSV válido")

    contenido = archivo.file.read().decode("utf-8")
    lector = csv.DictReader(io.StringIO(contenido))

    nuevos = 0
    for fila in lector:
        try:
            producto = Producto(
                nombre=fila["Nombre"],
                clasificacion=fila.get("Clasificación"),
                tipo_producto=fila.get("Tipo"),
                estado=fila.get("Estado", "Activo"),
                impuestos=float(fila.get("Impuestos", 19)),
                codigo_sku=fila.get("Código SKU"),
                marca=fila.get("Marca"),
                precio=float(fila.get("Precio", 0)),
                cantidad=int(fila.get("Cantidad", 0)),
                sucursal_id=int(fila.get("Sucursal_ID", 1))  # ⚠️ debes tener al menos una sucursal con id=1
            )
            db.add(producto)
            nuevos += 1
        except Exception as e:
            print(f"⚠️ Error en fila: {fila} → {e}")

    db.commit()
    return {"mensaje": f"Importación completada: {nuevos} productos agregados"}

# ============================================================
# 🧾 EXPORTAR PRODUCTOS EN TXT (opcional)
# ============================================================

@router.get("/exportar/txt")
def exportar_txt(
    db: Session = Depends(get_db),
    _: dict = Depends(verificar_token)
):
    """
    Exporta los productos en formato TXT (texto plano, legible).
    """
    productos = db.query(Producto).all()
    if not productos:
        # Evita que 404 dispare un error CORS
        return StreamingResponse(
            io.StringIO("No hay productos registrados. "),
            media_type="text/plain",
            headers={"Content-Disposition": "Attachment; filename=sin_datos.txt"}
        )

    salida = io.StringIO()
    for p in productos:
        salida.write(
            f"ID: {p.id} | {p.nombre} | {p.marca or '-'} | ${p.precio} | Stock: {p.cantidad}\n"
        )

    salida.seek(0)
    return StreamingResponse(
        salida,
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=inventario.txt"}
    )
