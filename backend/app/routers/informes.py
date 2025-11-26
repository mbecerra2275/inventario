from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.producto_model import Producto
from app.models.sucursal_model import Sucursal
import pandas as pd
import io
import datetime

router = APIRouter(prefix="/informes", tags=["Informes"])


# ============================================================
# 📤 EXPORTAR CSV
# ============================================================
@router.get("/exportar/csv")
def exportar_csv(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()

    data = [
        {
            "nombre": p.nombre,
            "clasificacion": p.clasificacion,
            "tipo_producto": p.tipo_producto,
            "estado": p.estado,
            "impuestos": p.impuestos,
            "codigo_sku": p.codigo_sku,
            "marca": p.marca,
            "precio": p.precio,
            "cantidad": p.cantidad,
            "sucursal_id": p.sucursal_id,
            "costo_neto_unitario": p.costo_neto_unitario,
            "costo_neto_total": p.costo_neto_total,
            "doc_recepcion_ing": p.doc_recepcion_ing,
        }
        for p in productos
    ]

    df = pd.DataFrame(data)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=productos.csv"},
    )


# ============================================================
# 📤 EXPORTAR TXT
# ============================================================
@router.get("/exportar/txt")
def exportar_txt(db: Session = Depends(get_db)):
    productos = db.query(Producto).all()
    buffer = io.StringIO()

    for p in productos:
        buffer.write(
            f"{p.codigo_sku} | {p.nombre} | {p.precio} | {p.cantidad} | Sucursal: {p.sucursal_id}\n"
        )

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/plain",
        headers={"Content-Disposition": "attachment; filename=productos.txt"},
    )


# ============================================================
# 📥 IMPORTAR ARCHIVO (CSV o Excel XLSX) con UPSERT
# ============================================================
@router.post("/importar/csv")
def importar_archivo(archivo: UploadFile = File(...), db: Session = Depends(get_db)):

    extension = archivo.filename.split(".")[-1].lower()
    if extension not in ["csv", "xlsx"]:
        raise HTTPException(status_code=400, detail="Solo se permiten archivos CSV o Excel (.xlsx)")

    # ---------------------- LEER ARCHIVO ----------------------
    try:
        if extension == "csv":
            df = pd.read_csv(archivo.file, dtype=str)
        else:
            df = pd.read_excel(archivo.file, dtype=str)
    except Exception:
        raise HTTPException(status_code=400, detail="Archivo inválido o corrupto")

    df = df.fillna("")  # Evita valores NaN

    insertados = 0
    actualizados = 0
    errores = 0

    for _, row in df.iterrows():

        try:
            sku = str(row.get("codigo_sku", "")).strip()

            if sku == "":
                errores += 1
                continue

            # Conversión segura
            precio = float(row.get("precio", 0) or 0)
            cantidad = int(float(row.get("cantidad", 0) or 0))

            sucursal_id = row.get("sucursal_id", "1").strip()
            sucursal_id = int(sucursal_id) if sucursal_id.isdigit() else 1

            # Validar sucursal existente
            if not db.query(Sucursal).filter_by(id=sucursal_id).first():
                errores += 1
                continue

            # UPSERT: buscar producto por SKU
            producto = db.query(Producto).filter_by(codigo_sku=sku).first()

            if producto:
                # ---------------- ACTUALIZAR ----------------
                producto.nombre = row.get("nombre", "")
                producto.clasificacion = row.get("clasificacion", "")
                producto.tipo_producto = row.get("tipo_producto", "")
                producto.estado = row.get("estado", "Activo")
                producto.impuestos = float(row.get("impuestos", 0) or 0)
                producto.marca = row.get("marca", "")
                producto.precio = precio
                producto.cantidad = cantidad
                producto.sucursal_id = sucursal_id
                producto.costo_neto_unitario = float(row.get("costo_neto_unitario", 0) or 0)
                producto.costo_neto_total = float(row.get("costo_neto_total", 0) or 0)
                producto.doc_recepcion_ing = row.get("doc_recepcion_ing", "SIN-DOC")

                actualizados += 1

            else:
                # ---------------- INSERTAR ----------------
                nuevo = Producto(
                    nombre=row.get("nombre", ""),
                    clasificacion=row.get("clasificacion", ""),
                    tipo_producto=row.get("tipo_producto", ""),
                    estado=row.get("estado", "Activo"),
                    impuestos=float(row.get("impuestos", 0) or 0),
                    codigo_sku=sku,
                    marca=row.get("marca", ""),
                    precio=precio,
                    cantidad=cantidad,
                    sucursal_id=sucursal_id,
                    costo_neto_unitario=float(row.get("costo_neto_unitario", 0) or 0),
                    costo_neto_total=float(row.get("costo_neto_total", 0) or 0),
                    doc_recepcion_ing=row.get("doc_recepcion_ing", "SIN-DOC"),
                )
                db.add(nuevo)
                insertados += 1

            db.commit()

        except Exception as e:
            print(f"❌ Error fila: {row} → {e}")
            db.rollback()
            errores += 1

    return {
        "mensaje": "Importación finalizada",
        "insertados": insertados,
        "actualizados": actualizados,
        "errores": errores,
    }
