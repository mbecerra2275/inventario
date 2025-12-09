/* ============================================================
   📦 PRODUCTOS.JS — VERSIÓN OPTIMIZADA, DOCUMENTADA Y ORDENADA
   Autor: Milton Becerra
   Fecha: 2025
   ============================================================ */

/* ============================================================
   🔧 CONFIGURACIÓN INICIAL
   ============================================================ */
const API_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

// Selectores principales
const tabla = document.getElementById("tabla-productos");
const formProducto = document.getElementById("form-producto");

/* ============================================================
   💰 FORMATEAR MONEDA (PESO CHILENO)
   ============================================================ */
function formatearCLP(valor) {
    if (isNaN(valor)) return "$0";
    return new Intl.NumberFormat("es-CL", {
        style: "currency",
        currency: "CLP",
        minimumFractionDigits: 0,
    }).format(valor);
}

/* ============================================================
   📌 CARGAR LISTADO DE PRODUCTOS
   ============================================================ */
async function cargarProductos() {
    try {
        const response = await fetch(`${API_URL}/productos/`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Error al cargar productos");

        const productos = await response.json();
        tabla.innerHTML = "";

        productos.forEach(prod => tabla.appendChild(crearFilaProducto(prod)));

    } catch (error) {
        console.error("❌ Error al cargar productos:", error);
    }
}

/* ============================================================
   🧱 GENERAR FILA EN TABLA
   ============================================================ */
function crearFilaProducto(prod) {
    const tr = document.createElement("tr");

    tr.innerHTML = `
        <td>${prod.id}</td>
        <td>${prod.nombre}</td>
        <td>${prod.tipo_producto || "-"}</td>
        <td>${prod.clasificacion || "-"}</td>
        <td>${prod.estado}</td>
        <td>${prod.impuestos}%</td>
        <td>${prod.codigo_sku}</td>
        <td>${prod.marca || "-"}</td>
        <td><strong>${formatearCLP(prod.precio)}</strong></td>
        <td>${prod.cantidad}</td>
        <td>${prod.sucursal_id}</td>
        <td>${formatearCLP(prod.costo_neto_unitario)}</td>
        <td>${formatearCLP(prod.costo_neto_total)}</td>
        <td>${prod.doc_recepcion_ing}</td>
        <td>
            <button class="btn btn-warning btn-sm" onclick="editarProducto(${prod.id})">
                <i class="bi bi-pencil-square"></i>
            </button>
            <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${prod.id})">
                <i class="bi bi-trash"></i>
            </button>
        </td>
    `;
    return tr;
}

/* ============================================================
   📝 GENERAR FORMULARIO DE PRODUCTO
   ============================================================ */
function generarFormulario() {
    formProducto.innerHTML = `
        <div class="col-md-4">
            <label class="form-label">Nombre</label>
            <input id="nombre" class="form-control" required>
        </div>
        <div class="col-md-4">
            <label class="form-label">Clasificación</label>
            <input id="clasificacion" class="form-control">
        </div>
        <div class="col-md-4">
            <label class="form-label">Tipo Producto</label>
            <input id="tipo_producto" class="form-control">
        </div>

        <div class="col-md-3">
            <label class="form-label">Estado</label>
            <select id="estado" class="form-select">
                <option value="Activo">Activo</option>
                <option value="Inactivo">Inactivo</option>
            </select>
        </div>
        <div class="col-md-3">
            <label class="form-label">Impuestos (%)</label>
            <input id="impuestos" type="number" class="form-control" value="19">
        </div>
        <div class="col-md-3">
            <label class="form-label">Código SKU</label>
            <input id="codigo_sku" class="form-control" required>
        </div>
        <div class="col-md-3">
            <label class="form-label">Marca</label>
            <input id="marca" class="form-control">
        </div>

        <div class="col-md-3">
            <label class="form-label">Precio</label>
            <input id="precio" type="number" class="form-control">
        </div>
        <div class="col-md-3">
            <label class="form-label">Cantidad</label>
            <input id="cantidad" type="number" class="form-control">
        </div>
        <div class="col-md-3">
            <label class="form-label">Sucursal ID</label>
            <input id="sucursal_id" type="number" class="form-control">
        </div>
        <div class="col-md-3">
            <label class="form-label">Doc. Recepción</label>
            <input id="doc_recepcion_ing" class="form-control">
        </div>

        <div class="col-12 text-end mt-3">
            <button type="button" onclick="guardarProducto()" class="btn btn-success">
                <i class="bi bi-save"></i> Guardar
            </button>
        </div>
    `;
}

/* ============================================================
   💾 GUARDAR PRODUCTO
   ============================================================ */
async function guardarProducto() {
    const data = {
        nombre: nombre.value,
        clasificacion: clasificacion.value,
        tipo_producto: tipo_producto.value,
        estado: estado.value,
        impuestos: Number(impuestos.value),
        codigo_sku: codigo_sku.value,
        marca: marca.value,
        precio: Number(precio.value),
        cantidad: Number(cantidad.value),
        sucursal_id: Number(sucursal_id.value),
        doc_recepcion_ing: doc_recepcion_ing.value || "SIN-DOC",
    };

    try {
        const response = await fetch(`${API_URL}/productos/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error("Error al guardar producto");

        await cargarProductos();
        alert("Producto guardado correctamente");

    } catch (error) {
        console.error(error);
    }
}

/* ============================================================
   ✏ EDITAR PRODUCTO (CARGA AL FORMULARIO)
   ============================================================ */
async function editarProducto(id) {
    try {
        const response = await fetch(`${API_URL}/productos/${id}`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        const prod = await response.json();

        nombre.value = prod.nombre;
        clasificacion.value = prod.clasificacion;
        tipo_producto.value = prod.tipo_producto;
        estado.value = prod.estado;
        impuestos.value = prod.impuestos;
        codigo_sku.value = prod.codigo_sku;
        marca.value = prod.marca;
        precio.value = prod.precio;
        cantidad.value = prod.cantidad;
        sucursal_id.value = prod.sucursal_id;
        doc_recepcion_ing.value = prod.doc_recepcion_ing;

    } catch (error) {
        console.error("❌ Error al editar producto:", error);
    }
}

/* ============================================================
   🗑 ELIMINAR PRODUCTO
   ============================================================ */
async function eliminarProducto(id) {
    if (!confirm("¿Seguro que deseas eliminar este producto?")) return;

    try {
        const response = await fetch(`${API_URL}/productos/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.ok) throw new Error("Error al eliminar");

        cargarProductos();

    } catch (error) {
        console.error("❌ Error al eliminar:", error);
    }
}

/* ============================================================
   🚀 INICIALIZAR PÁGINA
   ============================================================ */
document.addEventListener("DOMContentLoaded", () => {
    generarFormulario();
    cargarProductos();
});
