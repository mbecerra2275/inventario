// ================================================================
// Dashboard.js - versión final unificada
// ================================================================

const API_BASE = "http://127.0.0.1:8000";

function buildHeaders() {
  const token = localStorage.getItem("token");
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
}

document.addEventListener("DOMContentLoaded", () => {
  cargarMetricasDashboard();
  cargarGraficoCategorias();
  cargarProductosRecientes();
  cargarSucursalesActivas();
});

// ------------------------------------------------------------
// MÉTRICAS DE LAS CARDS
// ------------------------------------------------------------
async function cargarMetricasDashboard() {
  try {
    const resp = await fetch(`${API_BASE}/dashboard/metricas`, {
      headers: buildHeaders()
    });

    if (!resp.ok) throw new Error("Error al obtener métricas");

    const data = await resp.json();

    setTextIfExists("stockBajo", data.stock_bajo);
    setTextIfExists("sucursalesActivas", data.sucursales_activas);
    setTextIfExists("totalProductos", data.total_productos);
    setTextIfExists("productosNuevos", data.productos_nuevos);

  } catch (err) {
    console.error("Error cargando métricas avanzadas:", err);
  }
}

// ------------------------------------------------------------
// GRÁFICO DE CATEGORÍAS
// ------------------------------------------------------------
async function cargarGraficoCategorias() {
  try {
    const resp = await fetch(`${API_BASE}/dashboard/categorias/distribucion`, {
      headers: buildHeaders()
    });

    if (!resp.ok) throw new Error("Error al obtener categorías");

    const data = await resp.json();
    if (!data || !data.length) return;

    const labels = data.map(d => d.categoria);
    const values = data.map(d => d.total);

    const canvas = document.getElementById("chartCategorias");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    // eslint-disable-next-line no-undef
    new Chart(ctx, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: [
            "#2ecc71",
            "#3498db",
            "#9b59b6",
            "#f1c40f",
            "#e67e22",
            "#e74c3c"
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { position: "bottom" }
        }
      }
    });

  } catch (err) {
    console.error("Error cargando gráfico:", err);
  }
}

// ------------------------------------------------------------
// ÚLTIMOS 5 PRODUCTOS
// ------------------------------------------------------------
async function cargarProductosRecientes() {
  const tbody = document.getElementById("tabla-recientes");
  if (!tbody) return;

  try {
    const resp = await fetch(`${API_BASE}/productos/recientes?limit=5`, {
      headers: buildHeaders()
    });

    if (!resp.ok) throw new Error("Error al obtener productos recientes");

    const productos = await resp.json();
    tbody.innerHTML = "";

    if (!productos.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center text-muted">
            No hay productos recientes
          </td>
        </tr>`;
      return;
    }

    productos.forEach(p => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${p.nombre || "—"}</td>
        <td>${p.clasificacion || "—"}</td>
        <td>${formatearFecha(p.fecha_creacion)}</td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error cargando productos recientes:", err);
  }
}

// ------------------------------------------------------------
// SUCURSALES ACTIVAS
// ------------------------------------------------------------
async function cargarSucursalesActivas() {
  const tbody = document.getElementById("tabla-sucursales");
  if (!tbody) return;

  try {
    const resp = await fetch(`${API_BASE}/dashboard/sucursales/activas`, {
      headers: buildHeaders()
    });

    if (!resp.ok) throw new Error("Error al obtener sucursales");

    const sucursales = await resp.json();
    tbody.innerHTML = "";

    if (!sucursales.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="text-center text-muted">
            No hay sucursales activas
          </td>
        </tr>`;
      return;
    }

    sucursales.forEach(s => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${s.nombre || "—"}</td>
        <td>${s.direccion || "—"}</td>
        <td><span class="badge bg-success">Activa</span></td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error cargando sucursales:", err);
  }
}

// ------------------------------------------------------------
// UTILIDADES
// ------------------------------------------------------------
function setTextIfExists(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value ?? "-";
}

function formatearFecha(fecha) {
  if (!fecha) return "—";
  return new Date(fecha).toLocaleDateString("es-CL");
}
