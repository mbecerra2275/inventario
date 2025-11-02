// =====================================================
// 🔐 CONFIGURACIÓN DE LOGIN
// =====================================================
const API_URL = "http://127.0.0.1:8000";

// =====================================================
// 🚪 EVENTO: Envío del formulario de login
// =====================================================
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const alerta = document.getElementById("alertaLogin");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    alerta.classList.add("d-none");

    const correo = document.getElementById("correo").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!correo || !password) {
      mostrarAlerta("Por favor, ingresa tus credenciales.", "warning");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/usuarios/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ correo, password }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log("✅ Login exitoso:", data);
        // Guardar datos en localStorage
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("nombre", data.nombre);
        localStorage.setItem("rol", data.rol);

        mostrarAlerta("Inicio de sesión exitoso ✅", "success");

        // Redirigir tras un pequeño retardo
        setTimeout(() => {
          window.location.href = "index.html";
        }, 1000);
      } else {
        mostrarAlerta(data.detail || "Credenciales incorrectas", "danger");
      }
    } catch (error) {
      console.error("❌ Error en la solicitud:", error);
      mostrarAlerta("Error al conectar con el servidor.", "danger");
    }
  });
});

// =====================================================
// 📢 FUNCIÓN AUXILIAR
// =====================================================
function mostrarAlerta(mensaje, tipo) {
  const alerta = document.getElementById("alertaLogin");
  alerta.className = `alert alert-${tipo}`;
  alerta.textContent = mensaje;
  alerta.classList.remove("d-none");
}
