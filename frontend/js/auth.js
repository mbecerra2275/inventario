// ============================================================
// auth.js - Validación de sesión + Refresh automático + Roles
// Versión final (FASE 1,2,3,4 integrada)
// ============================================================

const API_VERIFICAR = "http://127.0.0.1:8000/auth/verificar";
const API_REFRESH = "http://127.0.0.1:8000/auth/refresh";

let refreshIntervalId = null;

// ------------------------------------------------------------
// VALIDAR SESIÓN (fix: usa ?token= para compatibilidad backend)
// ------------------------------------------------------------
async function validarSesion() {
  const token = localStorage.getItem("token");
  const nombreGuardado = localStorage.getItem("nombre");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    const response = await fetch(`${API_VERIFICAR}?token=${token}`);

    if (!response.ok) {
      localStorage.clear();
      window.location.href = "login.html";
      return;
    }

    const data = await response.json();

    // Normalizar
    if (data.nombre) localStorage.setItem("nombre", data.nombre);
    if (data.rol) localStorage.setItem("rol", data.rol.toLowerCase());

    // Mostrar nombre si corresponde
    const elementoNombre = document.getElementById("nombreUsuario");
    if (elementoNombre) elementoNombre.textContent = nombreGuardado || data.nombre || "Usuario";

    // Intentar renovar token
    await refreshToken();

    return data;

  } catch (error) {
    console.error("❌ Error en validarSesion()", error);
    localStorage.clear();
    window.location.href = "login.html";
  }
}

// ------------------------------------------------------------
// REFRESH TOKEN AUTOMÁTICO
// ------------------------------------------------------------
async function refreshToken() {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const response = await fetch(API_REFRESH, {
      headers: { "Authorization": `Bearer ${token}` }
    });

    if (response.ok) {
      const data = await response.json();
      if (data.token) {
        localStorage.setItem("token", data.token);
      }
    }
  } catch (error) {
    console.warn("⚠️ Error en refreshToken():", error);
  }
}

// ------------------------------------------------------------
// AUTO-REFRESH CADA N MINUTOS
// ------------------------------------------------------------
function iniciarAutoRefreshSesion(intervaloMinutos = 20) {
  if (refreshIntervalId !== null) return;

  refreshIntervalId = setInterval(() => {
    refreshToken();
  }, intervaloMinutos * 60 * 1000);
}

// ------------------------------------------------------------
// PROTEGER PÁGINA SEGÚN ROL
// ------------------------------------------------------------
function protegerPagina(rolesPermitidos) {
  const rol = (localStorage.getItem("rol") || "").toLowerCase();

  if (!rolesPermitidos.includes(rol)) {
    alert("Acceso no autorizado");
    window.location.href = "index.html";
  }
}

