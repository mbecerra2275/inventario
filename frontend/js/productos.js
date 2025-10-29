const API_URL = "http://127.0.0.1:8000/productos";
let paginaActual = 0;
const limite = 50;
let todosLosProductos = [];

async function cargarProductos() {
  try {
    const skip = paginaActual * limite;
    const response = await fetch(`${API_URL}?skip=${skip}&limit=${limite}`);
    if (!response.ok) throw new Error("Error al cargar productos");
    const productos = await response.json();
    todosLosProductos = productos;
    mostrarProductos(productos);
    actualizarControles(productos.length);
  } catch (error) {
    console.error("❌ Error al obtener productos:", error);
    document.getElementById("tablaProductos").innerHTML =
      `<tr><td colspan="9" class="text-center text-danger">Error al cargar productos</td></tr>`;
  }
}

function mostrarProductos(productos) {
  const tbody = document.getElementById("tablaProductos");
  if (!tbody) return;

  if (productos.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">No hay productos disponibles</td></tr>`;
    return;
  }

  tbody.innerHTML = productos.map(p => `
    <tr>
      <td>${p.id}</td>
      <td>${p.codigo_sku || "-"}</td>
      <td><strong>${p.nombre}</strong></td>
      <td>${p.marca || "-"}</td>
      <td>${p.clasificacion || "-"}</td>
      <td>${new Intl.NumberFormat("es-CL").format(p.precio)}</td>
      <td>${p.cantidad}</td>
      <td>${new Date(p.fecha_creacion).toLocaleDateString('es-CL')}</td>
      <td>
        <button class="btn btn-warning btn-sm" onclick="editarProducto(${p.id})">
          <i class="bi bi-pencil"></i>
        </button>
        <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${p.id})">
          <i class="bi bi-trash"></i>
        </button>
      </td>
    </tr>
  `).join('');
}

function actualizarControles(numProductos) {
  document.getElementById("paginaInfo").textContent =
    `Página ${paginaActual + 1}`;
  document.getElementById("btnAnterior").disabled = paginaActual === 0;
  document.getElementById("btnSiguiente").disabled = numProductos < limite;
}

// =======================
// 🔍 FILTRO LOCAL
// =======================
function filtrarProductos() {
  const nombre = document.getElementById("filtroNombre").value.toLowerCase();
  const sku = document.getElementById("filtroSKU").value.toLowerCase();
  const marca = document.getElementById("filtroMarca").value.toLowerCase();
  const fecha = document.getElementById("filtroFecha").value;

  let filtrados = todosLosProductos.filter(p => {
    const coincideNombre = p.nombre?.toLowerCase().includes(nombre);
    const coincideSKU = p.codigo_sku?.toLowerCase().includes(sku);
    const coincideMarca = p.marca?.toLowerCase().includes(marca);
    const coincideFecha = !fecha || p.fecha_creacion.startsWith(fecha);
    return coincideNombre && coincideSKU && coincideMarca && coincideFecha;
  });

  mostrarProductos(filtrados);
}

document.getElementById("btnBuscar").addEventListener("click", filtrarProductos);
document.getElementById("btnAnterior").addEventListener("click", () => {
  if (paginaActual > 0) {
    paginaActual--;
    cargarProductos();
  }
});
document.getElementById("btnSiguiente").addEventListener("click", () => {
  paginaActual++;
  cargarProductos();
});
document.addEventListener("DOMContentLoaded", cargarProductos);
