// ============================================================
// 📊 Informes y Plantillas – Sistema de Inventario
// ============================================================

const API_URL = "http://127.0.0.1:8000";
let token = localStorage.getItem("token");

const btnExportCSV = document.getElementById("btnExportCSV");
const btnExportTXT = document.getElementById("btnExportTXT");
const btnImport = document.getElementById("btnImport");
const inputFile = document.getElementById("inputFile");
const resultado = document.getElementById("resultado");

// ============================================================
// 🧾 Función auxiliar: mostrar mensajes en pantalla
// ============================================================
function mostrarMensaje(tipo, mensaje) {
  resultado.innerHTML = `<div class="alert alert-${tipo} mt-3">${mensaje}</div>`;
}

// ============================================================
// 🔄 Renovar token automáticamente
// ============================================================
async function renovarToken() {
  const tokenActual = localStorage.getItem("token");
  if (!tokenActual) return null;

  try {
    const response = await fetch(`${API_URL}/auth/refresh`, {
      headers: { Authorization: `Bearer ${tokenActual}` },
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem("token", data.token);
      token = data.token;
      console.log("🔄 Token renovado correctamente");
      return data.token;
    } else {
      console.warn("No se pudo renovar el token:", response.status);
      return null;
    }
  } catch (error) {
    console.error("Error al renovar token:", error);
    return null;
  }
}

// ============================================================
// 📤 Descargar CSV
// ============================================================
btnExportCSV.addEventListener("click", async () => {
  if (!token) {
    mostrarMensaje("warning", "⚠️ Debes iniciar sesión para exportar datos.");
    return;
  }

  try {
    let response = await fetch(`${API_URL}/informes/exportar/csv`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    // Si el token expiró, intentamos renovarlo automáticamente
    if (response.status === 401) {
      const nuevoToken = await renovarToken();
      if (!nuevoToken) {
        mostrarMensaje("danger", "⚠️ Tu sesión expiró. Inicia sesión nuevamente.");
        return;
      }
      response = await fetch(`${API_URL}/informes/exportar/csv`, {
        headers: { Authorization: `Bearer ${nuevoToken}` },
      });
    }

    if (!response.ok) throw new Error(`Error ${response.status}`);

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "productos_inventario.csv";
    a.click();
    mostrarMensaje("success", "📦 Archivo CSV descargado correctamente.");
  } catch (error) {
    console.error(error);
    mostrarMensaje("danger", "❌ Error al descargar CSV.");
  }
});

// ============================================================
// 📄 Descargar TXT
// ============================================================
btnExportTXT.addEventListener("click", async () => {
  if (!token) {
    mostrarMensaje("warning", "⚠️ Debes iniciar sesión para exportar datos.");
    return;
  }

  try {
    let response = await fetch(`${API_URL}/informes/exportar/txt`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    // Intentar renovar si el token expiró
    if (response.status === 401) {
      const nuevoToken = await renovarToken();
      if (!nuevoToken) {
        mostrarMensaje("danger", "⚠️ Tu sesión expiró. Inicia sesión nuevamente.");
        return;
      }
      response = await fetch(`${API_URL}/informes/exportar/txt`, {
        headers: { Authorization: `Bearer ${nuevoToken}` },
      });
    }

    if (!response.ok) throw new Error(`Error ${response.status}`);

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "productos_inventario.txt";
    a.click();
    mostrarMensaje("success", "📄 Archivo TXT descargado correctamente.");
  } catch (error) {
    console.error(error);
    mostrarMensaje("danger", "❌ Error al descargar TXT.");
  }
});

// ============================================================
// 📥 Importar CSV
// ============================================================
btnImport.addEventListener("click", async () => {
  const file = inputFile.files[0];
  if (!file) {
    mostrarMensaje("warning", "⚠️ Selecciona un archivo CSV primero.");
    return;
  }

  if (!token) {
    mostrarMensaje("warning", "⚠️ Debes iniciar sesión para importar datos.");
    return;
  }

  const formData = new FormData();
  formData.append("archivo", file);

  try {
    let response = await fetch(`${API_URL}/informes/importar/csv`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (response.status === 401) {
      const nuevoToken = await renovarToken();
      if (!nuevoToken) {
        mostrarMensaje("danger", "⚠️ Tu sesión expiró. Inicia sesión nuevamente.");
        return;
      }
      response = await fetch(`${API_URL}/informes/importar/csv`, {
        method: "POST",
        headers: { Authorization: `Bearer ${nuevoToken}` },
        body: formData,
      });
    }

    if (!response.ok) {
      const msg = await response.text();
      throw new Error(msg);
    }

    const data = await response.json();
    mostrarMensaje("success", `✅ ${data.mensaje}`);
  } catch (error) {
    console.error(error);
    mostrarMensaje("danger", "❌ Error al importar CSV.");
  }
});
