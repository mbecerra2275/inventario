// ========================================
// CONFIGURACIÓN DE LA API
// ========================================
const API_URL = "http://127.0.0.1:8000";

// ========================================
// UTILIDADES
// ========================================

// Formatear número en pesos CLP
function formatearCLP(numero) {
  return new Intl.NumberFormat("es-CL", {
    style: "currency",
    currency: "CLP",
    minimumFractionDigits: 0,
  }).format(numero);
}

// Formatear fecha
function formatearFecha(fecha) {
  return new Date(fecha).toLocaleDateString("es-CL", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

// Badge de estado
function getBadgeEstado(estado) {
  const badges = {
    Activo: "badge bg-success",
    Inactivo: "badge bg-secondary",
    Descontinuado: "badge bg-danger",
  };
  return `<span class="${badges[estado] || "badge bg-success"}">${estado}</span>`;
}

// Mostrar alerta visual
function mostrarAlerta(mensaje, tipo = "info") {
  const alert = document.getElementById("alert");
  if (!alert) return;

  alert.textContent = mensaje;
  alert.className = `alert alert-${tipo}`;
  alert.classList.remove("d-none");

  setTimeout(() => alert.classList.add("d-none"), 4000);
}

// ========================================
// CARGA SEGURA AL INICIAR
// ========================================
document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ DOM completamente cargado. Iniciando aplicación...");

  const token = localStorage.getItem("token");
  if (!token) {
    console.warn("⚠️ No hay sesión iniciada. Redirigiendo al login...");
    window.location.href = "login.html";
    return;
  }

  // Mostrar nombre y rol
  const nombreUsuario = document.getElementById("nombreUsuario");
  const rolUsuario = document.getElementById("rolUsuario");
  if (nombreUsuario && rolUsuario) {
    nombreUsuario.textContent = localStorage.getItem("nombre") || "Usuario";
    rolUsuario.textContent = `Rol: ${localStorage.getItem("rol") || "Invitado"}`;
  }

  // Cargar productos
  setTimeout(() => cargarProductos(), 400);
});

// ========================================
// 📦 FUNCIÓN PRINCIPAL: CARGAR PRODUCTOS
// ========================================
async function cargarProductos(reintento = 0) {
  const tabla = document.getElementById("tablaProductos");

  if (!tabla) {
    console.warn("⌛ Esperando que la tabla se cargue en el DOM...");
    if (reintento < 5) {
      setTimeout(() => cargarProductos(reintento + 1), 300);
    } else {
      console.error("❌ No se encontró la tabla después de varios intentos.");
    }
    return;
  }

  try {
    console.log("📡 Solicitando productos al backend...");
    const response = await fetch(`${API_URL}/productos`);

    if (!response.ok) {
      console.error(`⚠️ Error HTTP ${response.status}`);
      tabla.innerHTML =
        '<tr><td colspan="13" class="text-center text-danger">Error al cargar productos desde el servidor</td></tr>';
      return;
    }

    const productos = await response.json();
    console.log(`✅ ${productos.length} productos recibidos`);

    if (productos.length === 0) {
      tabla.innerHTML =
        '<tr><td colspan="13" class="text-center text-muted">No hay productos registrados</td></tr>';
      return;
    }

    tabla.innerHTML = productos
      .map(
        (p) => `
        <tr>
          <td>${p.id}</td>
          <td>${p.codigo_sku || "-"}</td>
          <td><strong>${p.nombre}</strong></td>
          <td>${p.marca || "-"}</td>
          <td>${p.clasificacion || "-"}</td>
          <td>${p.tipo_producto || "-"}</td>
          <td>${getBadgeEstado(p.estado)}</td>
          <td>${formatearCLP(p.precio)}</td>
          <td>${p.cantidad}</td>
          <td>${p.impuestos}%</td>
          <td>${formatearCLP(p.precio * p.cantidad)}</td>
          <td>${formatearFecha(p.fecha_creacion)}</td>
          <td>
            <button class="btn btn-warning btn-sm" onclick="editarProducto(${p.id})">
              <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${p.id})">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>`
      )
      .join("");

    actualizarEstadisticas(productos);
  } catch (error) {
    console.error("❌ Error de conexión:", error);
    tabla.innerHTML =
      '<tr><td colspan="13" class="text-center text-danger">No se pudo conectar al backend</td></tr>';

    if (reintento < 3) {
      console.warn("🔁 Reintentando conexión...");
      setTimeout(() => cargarProductos(reintento + 1), 1000);
    }
  }
}

// ========================================
// 📊 ESTADÍSTICAS
// ========================================
function actualizarEstadisticas(productos) {
  const total = productos.length;
  const stock = productos.reduce((s, p) => s + p.cantidad, 0);
  const valor = productos.reduce((s, p) => s + p.precio * p.cantidad, 0);

  document.getElementById("totalProductos").textContent = total;
  document.getElementById("totalStock").textContent = stock;
  document.getElementById("valorInventario").textContent = formatearCLP(valor);
}

// ========================================
// 🔍 BÚSQUEDA
// ========================================
function buscarProducto() {
  const busqueda = document.getElementById("buscar").value.toLowerCase();
  const filas = document.querySelectorAll("#tablaProductos tr");
  filas.forEach((fila) => {
    const texto = fila.textContent.toLowerCase();
    fila.style.display = texto.includes(busqueda) ? "" : "none";
  });
}

// ========================================
// 🧾 CRUD: CREAR / EDITAR / ELIMINAR
// ========================================
async function crearProducto(producto) {
  const response = await fetch(`${API_URL}/productos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(producto),
  });

  if (response.ok) {
    mostrarAlerta("Producto creado correctamente", "success");
    cargarProductos();
  } else {
    const error = await response.json();
    mostrarAlerta(error.detail || "Error al crear producto", "danger");
  }
}

async function editarProducto(id) {
  const res = await fetch(`${API_URL}/productos/${id}`);
  const producto = await res.json();

  document.getElementById("productoId").value = producto.id;
  document.getElementById("nombre").value = producto.nombre;
  document.getElementById("codigo_sku").value = producto.codigo_sku || "";
  document.getElementById("marca").value = producto.marca || "";
  document.getElementById("clasificacion").value = producto.clasificacion || "";
  document.getElementById("tipo_producto").value = producto.tipo_producto || "";
  document.getElementById("estado").value = producto.estado;
  document.getElementById("precio").value = producto.precio;
  document.getElementById("cantidad").value = producto.cantidad;
  document.getElementById("impuestos").value = producto.impuestos;

  document.getElementById("formTitle").textContent = "✏️ Editar Producto";
  document.getElementById("btnSubmit").textContent = "Actualizar Producto";
  document.getElementById("btnCancelar").classList.remove("d-none");
}

async function actualizarProducto(id, producto) {
  const response = await fetch(`${API_URL}/productos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(producto),
  });

  if (response.ok) {
    mostrarAlerta("Producto actualizado", "success");
    cancelarEdicion();
    cargarProductos();
  } else {
    const error = await response.json();
    mostrarAlerta(error.detail || "Error al actualizar producto", "danger");
  }
}

async function eliminarProducto(id) {
  if (!confirm("¿Seguro que deseas eliminar este producto?")) return;
  const response = await fetch(`${API_URL}/productos/${id}`, { method: "DELETE" });

  if (response.ok) {
    mostrarAlerta("Producto eliminado", "success");
    cargarProductos();
  } else {
    mostrarAlerta("Error al eliminar producto", "danger");
  }
}

// ========================================
// 🔄 CANCELAR EDICIÓN
// ========================================
function cancelarEdicion() {
  document.getElementById("productoForm").reset();
  document.getElementById("productoId").value = "";
  document.getElementById("btnCancelar").classList.add("d-none");
  document.getElementById("formTitle").textContent = "➕ Agregar Nuevo Producto";
  document.getElementById("btnSubmit").textContent = "Guardar Producto";
}

// ========================================
// 🚪 CERRAR SESIÓN
// ========================================
function cerrarSesion() {
  localStorage.clear();
  window.location.href = "login.html";
}
// ========================================
// 🧾 EVENTO: ENVÍO DEL FORMULARIO DE PRODUCTO
// ========================================
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("productoForm");

  if (!form) {
    console.error("❌ No se encontró el formulario con id 'productoForm'");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("📤 Enviando formulario de producto...");

    const id = document.getElementById("productoId").value;
    const producto = {
      nombre: document.getElementById("nombre").value,
      codigo_sku: document.getElementById("codigo_sku").value || null,
      marca: document.getElementById("marca").value || null,
      clasificacion: document.getElementById("clasificacion").value || null,
      tipo_producto: document.getElementById("tipo_producto").value || null,
      estado: document.getElementById("estado").value,
      precio: parseFloat(document.getElementById("precio").value),
      cantidad: parseInt(document.getElementById("cantidad").value),
      impuestos: parseFloat(document.getElementById("impuestos").value),
    };

    try {
      if (id) {
        console.log("✏️ Actualizando producto existente:", id);
        await actualizarProducto(id, producto);
      } else {
        console.log("➕ Creando nuevo producto:", producto);
        await crearProducto(producto);
      }
    } catch (error) {
      console.error("❌ Error al guardar producto:", error);
      mostrarAlerta("Error al guardar producto", "danger");
    }
  });
});
