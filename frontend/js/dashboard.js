const API_URL = "http://127.0.0.1:8000";

async function cargarMetricas() {
  console.log("📊 Cargando métricas generales...");

  try {
    const response = await fetch(`${API_URL}/productos/`);
    if (!response.ok) throw new Error("Error al obtener productos");

    const productos = await response.json();

    const totalProductos = productos.length;
    const stockTotal = productos.reduce((acc, p) => acc + (p.cantidad || 0), 0);
    const ventasMes = 0; // ⚙️ Pendiente de conectar módulo de ventas

    document.getElementById("totalProductos").textContent = totalProductos;
    document.getElementById("stockTotal").textContent = stockTotal;
    document.getElementById("ventasMes").textContent = `$${ventasMes}`;
  } catch (error) {
    console.error("❌ Error al cargar métricas:", error);
  }
}

document.addEventListener("DOMContentLoaded", cargarMetricas);
