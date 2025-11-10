// =====================================================
// 🔒 VERIFICAR SESIÓN EN CADA PÁGINA PRIVADA
// =====================================================
const API_AUTH = "http://127.0.0.1:8000/auth/verificar";

async function verificarSesion() {
  const token = localStorage.getItem("token");
  const nombre = localStorage.getItem("nombre");

  // Si no hay token, redirigir al login
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    const response = await fetch(`${API_AUTH}?token=${token}`);
    if (!response.ok) {
      localStorage.clear();
      window.location.href = "login.html";
      return;
    }

    const data = await response.json();
    console.log("✅ Sesión válida:", data);

    // Mostrar el nombre del usuario si existe
    const nombreUsuario = document.getElementById("nombreUsuario");
    if (nombreUsuario) nombreUsuario.textContent = nombre || "Usuario";
  } catch (error) {
    console.error("❌ Error al verificar sesión:", error);
    localStorage.clear();
    window.location.href = "login.html";
  }
}
