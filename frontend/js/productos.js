// frontend/js/productos.js
const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  cargarSucursales();
  cargarProductos();

  const form = document.getElementById("productoForm");
  form.addEventListener("submit", onSubmitProducto);
});

// ----------------------------------------------------
// 🔹 Cargar sucursales en el select
// ----------------------------------------------------
async function cargarSucursales() {
  const sel = document.getElementById("sucursal");
  sel.innerHTML = `<option value="">Sin asignar</option>`;
  try {
    const res = await fetch(`${API_BASE}/sucursales/`);
    if (!res.ok) return;
    const data = await res.json();
    data.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s.id;
      opt.textContent = s.nombre;
      sel.appendChild(opt);
    });
  } catch (err) {
    console.error("❌ Error cargando sucursales:", err);
  }
}

// ----------------------------------------------------
// 🔹 Cargar productos en la tabla
// ----------------------------------------------------
async function cargarProductos() {
  const tbody = document.getElementById("tablaProductos");
  tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Cargando...</td></tr>`;

  try {
    const res = await fetch(`${API_BASE}/productos/`);
    if (!res.ok) throw new Error("No se pudo obtener productos");
    const productos = await res.json();

    // traer sucursales para mostrar nombre
    const resSuc = await fetch(`${API_BASE}/sucursales/`);
    const sucursales = resSuc.ok ? await resSuc.json() : [];
    const mapaSuc = {};
    sucursales.forEach(s => (mapaSuc[s.id] = s.nombre));

    tbody.innerHTML = "";
    productos.forEach(p => {
      const tr = document.createElement("tr");
      const sucursalNombre = p.sucursal_id ? (mapaSuc[p.sucursal_id] || `ID ${p.sucursal_id}`) : "—";

      tr.innerHTML = `
        <td>${p.id}</td>
        <td>${p.codigo_sku || "-"}</td>
        <td>${p.nombre}</td>
        <td>${p.marca || "-"}</td>
        <td>${sucursalNombre}</td>
        <td>$${p.precio.toLocaleString("es-CL")}</td>
        <td>${p.cantidad}</td>
        <td>
          <span class="badge ${p.estado === "Activo" ? "bg-success" : "bg-secondary"}">${p.estado}</span>
        </td>
        <td class="text-center">
          <button class="btn btn-sm btn-primary me-1" onclick="editarProducto(${p.id})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="eliminarProducto(${p.id})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("❌ Error cargando productos:", err);
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-danger">Error al cargar productos</td></tr>`;
  }
}

// ----------------------------------------------------
// 🔹 Crear / actualizar
// ----------------------------------------------------
async function onSubmitProducto(e) {
  e.preventDefault();

  const id = document.getElementById("productoId").value;
  const payload = {
    nombre: document.getElementById("nombre").value,
    codigo_sku: document.getElementById("codigo_sku").value || null,
    marca: document.getElementById("marca").value || null,
    precio: parseFloat(document.getElementById("precio").value),
    cantidad: parseInt(document.getElementById("cantidad").value),
    clasificacion: document.getElementById("clasificacion")?.value || null,
    tipo_producto: document.getElementById("tipo_producto")?.value || null,
    estado: document.getElementById("estado")?.value || "Activo",
    sucursal_id: document.getElementById("sucursal").value
      ? parseInt(document.getElementById("sucursal").value)
      : null,
    impuestos: 19.0
  };

  try {
    let res;
    if (id) {
      // actualizar
      res = await fetch(`${API_BASE}/productos/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    } else {
      // crear
      res = await fetch(`${API_BASE}/productos/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
    }

    if (!res.ok) {
      const err = await res.json();
      alert("⚠️ Error: " + (err.detail || "No se pudo guardar"));
      return;
    }

    document.getElementById("productoForm").reset();
    document.getElementById("productoId").value = "";
    cargarProductos();
  } catch (err) {
    console.error("❌ Error al guardar:", err);
  }
}

// ----------------------------------------------------
// 🔹 Editar
// ----------------------------------------------------
async function editarProducto(id) {
  try {
    const res = await fetch(`${API_BASE}/productos/${id}`);
    if (!res.ok) return;
    const p = await res.json();

    document.getElementById("productoId").value = p.id;
    document.getElementById("nombre").value = p.nombre;
    document.getElementById("codigo_sku").value = p.codigo_sku || "";
    document.getElementById("marca").value = p.marca || "";
    document.getElementById("precio").value = p.precio;
    document.getElementById("cantidad").value = p.cantidad;
    document.getElementById("clasificacion").value = p.clasificacion || "";
    document.getElementById("tipo_producto").value = p.tipo_producto || "";
    document.getElementById("estado").value = p.estado || "Activo";
    document.getElementById("sucursal").value = p.sucursal_id || "";
  } catch (err) {
    console.error("❌ Error al editar:", err);
  }
}

// ----------------------------------------------------
// 🔹 Eliminar
// ----------------------------------------------------
async function eliminarProducto(id) {
  if (!confirm("¿Deseas eliminar este producto?")) return;
  try {
    const res = await fetch(`${API_BASE}/productos/${id}`, { method: "DELETE" });
    if (res.ok) {
      cargarProductos();
    } else {
      alert("⚠️ No se pudo eliminar");
    }
  } catch (err) {
    console.error("❌ Error al eliminar:", err);
  }
}
