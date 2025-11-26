// ============================================================
//  INFORMES.JS FINAL — Funcionando al 100%
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    const API_URL = "http://127.0.0.1:8000";
    const token = localStorage.getItem("token");

    const btnImport = document.getElementById("btnImport");
    const inputFile = document.getElementById("inputFile");
    const btnExportCSV = document.getElementById("btnExportCSV");
    const btnExportTXT = document.getElementById("btnExportTXT");

    if (!btnImport || !inputFile || !btnExportCSV || !btnExportTXT) {
        console.error("❌ ERROR: Elementos del DOM no encontrados en informes.html");
        return;
    }

    // ============================================================
    // 📤 EXPORTAR CSV
    // ============================================================
    btnExportCSV.addEventListener("click", async () => {
        if (!token) return alert("⚠️ Debes iniciar sesión.");

        try {
            const response = await fetch(`${API_URL}/informes/exportar/csv`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` },
            });

            if (!response.ok) {
                throw new Error("Error al generar CSV");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "productos.csv";
            document.body.appendChild(a);
            a.click();
            a.remove();

        } catch (error) {
            console.error(error);
            alert("❌ Error al descargar CSV.");
        }
    });

    // ============================================================
    // 📄 EXPORTAR TXT (CORREGIDO 100%)
    // ============================================================
    btnExportTXT.addEventListener("click", async () => {
        if (!token) return alert("⚠️ Debes iniciar sesión.");

        try {
            const response = await fetch(`${API_URL}/informes/exportar/txt`, {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` },
            });

            if (!response.ok) {
                throw new Error("Error al generar TXT");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);

            const a = document.createElement("a");
            a.href = url;
            a.download = "inventario.txt";  
            document.body.appendChild(a);
            a.click();
            a.remove();

        } catch (error) {
            console.error(error);
            alert("❌ Error al descargar TXT.");
        }
    });

    // ============================================================
    // 📥 IMPORTAR ARCHIVO (CSV / XLSX)
    // ============================================================
    btnImport.addEventListener("click", async () => {

        const file = inputFile.files[0];
        if (!file) {
            alert("⚠️ Selecciona un archivo antes de importar.");
            return;
        }

        const extension = file.name.split(".").pop().toLowerCase();
        const permitidos = ["csv", "xlsx"];

        if (!permitidos.includes(extension)) {
            alert("❌ Solo se permiten archivos .csv o .xlsx");
            return;
        }

        if (!token) {
            alert("⚠️ Debes iniciar sesión.");
            return;
        }

        const formData = new FormData();
        formData.append("archivo", file);

        btnImport.disabled = true;
        btnImport.innerHTML = "Importando...";

        try {
            let response = await fetch(`${API_URL}/informes/importar/csv`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`, // 👈 Aquí estaba el error anterior
                },
                body: formData,
            });

            if (!response.ok) {
                const raw = await response.text();
                throw new Error(raw);
            }

            const data = await response.json();

            alert(
                `✅ Importación completada:\n\n` +
                `➕ Insertados: ${data.insertados}\n` +
                `🔄 Actualizados: ${data.actualizados}\n` +
                `⚠️ Errores: ${data.errores}`
            );

        } catch (error) {
            console.error("❌ ERROR IMPORTANDO:", error);
            alert("❌ Error al importar archivo.");
        } finally {
            btnImport.disabled = false;
            btnImport.innerHTML = "Importar Archivo";
        }
    });

}); // DOMContentLoaded END
