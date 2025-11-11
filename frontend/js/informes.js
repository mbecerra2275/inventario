const API_URL = "http://127.0.0.1:8000";
const token = localStorage.getItem("token");

const btnExportCSV = document.getElementById("btnExportCSV");
const btnExportTXT = document.getElementById("btnExportTXT");
const btnImport = document.getElementById("btnImport");
const inputFile = document.getElementById("inputFile");
const resultado = document.getElementById("resultado");

// --- Descargar CSV ---
btnExportCSV.addEventListener("click", async () => {
  try {
    const response = await fetch(`${API_URL}/informes/exportar/csv`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "productos_inventario.csv";
    a.click();
    resultado.innerHTML = `<div class="alert alert-success mt-3">📦 Archivo CSV descargado correctamente.</div>`;
  } catch (error) {
    console.error(error);
    resultado.innerHTML = `<div class="alert alert-danger mt-3">❌ Error al descargar CSV.</div>`;
  }
});

// --- Descargar TXT ---
btnExportTXT.addEventListener("click", async () => {
  try {
    const response = await fetch(`${API_URL}/informes/exportar/txt`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "productos_inventario.txt";
    a.click();
    resultado.innerHTML = `<div class="alert alert-success mt-3">📄 Archivo TXT descargado correctamente.</div>`;
  } catch (error) {
    console.error(error);
    resultado.innerHTML = `<div class="alert alert-danger mt-3">❌ Error al descargar TXT.</div>`;
  }
});

// --- Importar CSV ---
btnImport.addEventListener("click", async () => {
  const file = inputFile.files[0];
  if (!file) {
    resultado.innerHTML = `<div class="alert alert-warning mt-3">⚠️ Selecciona un archivo CSV primero.</div>`;
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_URL}/informes/importar/csv`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    const data = await response.json();
    resultado.innerHTML = `<div class="alert alert-success mt-3">✅ ${data.mensaje}</div>`;
  } catch (error) {
    console.error(error);
    resultado.innerHTML = `<div class="alert alert-danger mt-3">❌ Error al importar CSV.</div>`;
  }
});
