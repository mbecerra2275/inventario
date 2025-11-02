// ==============================================
// app.js — Gestión de Productos (CRUD Completo)
// Autor: Milton Becerra
// ==============================================

const API_URL = "http://127.0.0.1:8000";

// ===============================
// 🔹 1. Cargar productos
// ===============================
async function cargarProductos() {
  console.log("📦 Cargando productos...");

  const tabla = document.getElementById("tablaProductos");
  if (!tabla) {
    console.error("⚠️ No se encontró la tabla de productos en el DOM.");
    return;
  }

  try {
    const response = await fetch(`${API_URL}/productos/`);
    if (!response.ok) throw new Error("Error al obtener productos");
    const productos = await response.json();

    if (productos.length === 0) {
      tabla.innerHTML = `<tr><td colspan="8" class="text-center text-muted">No hay productos registrados</td></tr>`;
      return;
    }

    tabla.innerHTML = productos
      .map(
        (p) => `
      <tr>
        <td>${p.id}</td>
        <td>${p.nombre}</td>
        <td>${p.codigo_sku || "-"}</td>
        <td>$${p.precio.toLocaleString()}</td>
        <td>${p.cantidad}</td>
        <td>${p.marca || "-"}</td>
        <td>${sucursal}</td>
        <td>
          <span class="badge ${p.estado === "Activo" ? "bg-success" : "bg-secondary"}">
            ${p.estado}
          </span>
        </td>
        <td>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="editarProducto(${p.id})">
            <i class="bi bi-pencil"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger" onclick="eliminarProducto(${p.id})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      </tr>`
      )
      .join("");
  } catch (error) {
    console.error("❌ Error al cargar productos:", error);
    tabla.innerHTML = `<tr><td colspan="8" class="text-center text-danger">Error al conectar con el servidor</td></tr>`;
  }
}
// ========================================
// 🔹 CARGAR SUCURSALES DESDE LA API
// ========================================
async function cargarSucursales() {
  try {
    const response = await fetch(`${API_URL}/sucursales/`);
    if (!response.ok) throw new Error("Error al obtener sucursales");
    const sucursales = await response.json();

    const select = document.getElementById("sucursal");
    select.innerHTML = '<option value="">Seleccionar...</option>'; // limpiar y dejar opción inicial
    sucursales.forEach(s => {
      const option = document.createElement("option");
      option.value = s.id;
      option.textContent = `${s.nombre} (${s.ciudad || 'Sin ciudad'})`;
      select.appendChild(option);
    });

    console.log("✅ Sucursales cargadas:", sucursales.length);
  } catch (error) {
    console.error("❌ Error al cargar sucursales:", error);
  }
}


// ===============================
// 🔹 2. Crear nuevo producto
// ===============================
async function crearProducto(producto) {
  try {
    const response = await fetch(`${API_URL}/productos/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(producto),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Error al crear producto");
    }

    console.log("✅ Producto creado con éxito");
    await cargarProductos();
  } catch (error) {
    console.error("❌ Error al crear producto:", error);
    alert("Error: " + error.message);
  }
}

// ===============================
// 🔹 3. Actualizar producto
// ===============================
async function actualizarProducto(id, producto) {
  try {
    const response = await fetch(`${API_URL}/productos/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(producto),
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Error al actualizar producto");
    }

    console.log("✅ Producto actualizado");
    await cargarProductos();
  } catch (error) {
    console.error("❌ Error al actualizar producto:", error);
    alert("Error: " + error.message);
  }
}

// ===============================
// 🔹 4. Eliminar producto
// ===============================
async function eliminarProducto(id) {
  if (!confirm("¿Seguro que deseas eliminar este producto?")) return;

  try {
    const response = await fetch(`${API_URL}/productos/${id}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      const data = await response.json();
      throw new Error(data.detail || "Error al eliminar producto");
    }

    console.log("🗑️ Producto eliminado correctamente");
    await cargarProductos();
  } catch (error) {
    console.error("❌ Error al eliminar producto:", error);
    alert("Error: " + error.message);
  }
}

// ===============================
// 🔹 5. Editar producto
// ===============================
async function editarProducto(id) {
  try {
    const response = await fetch(`${API_URL}/productos/${id}`);
    if (!response.ok) throw new Error("Error al obtener producto");

    const producto = await response.json();
    document.getElementById("productoId").value = producto.id;
    document.getElementById("nombre").value = producto.nombre;
    document.getElementById("codigo_sku").value = producto.codigo_sku || "";
    document.getElementById("precio").value = producto.precio;
    document.getElementById("cantidad").value = producto.cantidad;
    document.getElementById("marca").value = producto.marca || "";
    document.getElementById("sucursal").value = producto.sucursal_id || "";
    document.getElementById("estado").value = producto.estado;
  } catch (error) {
    console.error("❌ Error al editar producto:", error);
    alert("Error al cargar datos del producto");
  }
}

// ===============================
// 🔹 6. Manejo del formulario
// ===============================
document.addEventListener("DOMContentLoaded", () => {
  cargarProductos();
  cargarSucursales();

  const form = document.getElementById("productoForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const id = document.getElementById("productoId").value;
    const producto = {
      nombre: document.getElementById("nombre").value.trim(),
      codigo_sku: document.getElementById("codigo_sku").value.trim(),
      precio: parseFloat(document.getElementById("precio").value),
      cantidad: parseInt(document.getElementById("cantidad").value),
      marca: document.getElementById("marca").value.trim(),
      sucursal_id: parseInt(document.getElementById("sucursal").value) || null,
      estado: document.getElementById("estado").value,
      impuestos: 19.0,
    };

    if (!producto.nombre || !producto.precio || !producto.cantidad) {
      alert("Por favor completa todos los campos obligatorios.");
      return;
    }

    if (id) {
      await actualizarProducto(id, producto);
    } else {
      await crearProducto(producto);
    }

    form.reset();
    document.getElementById("productoId").value = "";
  });
});

