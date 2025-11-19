// ============================================================
// auth.js - Validación de sesión + Refresh automático + Roles
// Versión FINAL (con fetchSeguro)
// ============================================================

const API_VERIFICAR = "http://127.0.0.1:8000/auth/verificar";
const API_REFRESH   = "http://127.0.0.1:8000/auth/refresh";

let refreshIntervalId = null;

// ------------------------------------------------------------
// 🧪 VALIDAR SESIÓN (usa ?token= para compatibilidad backend)
// ------------------------------------------------------------
async function validarSesion() {
  const token = localStorage.getItem("token");
  const nombreGuardado = localStorage.getItem("nombre");

  if (!token) {
    window.location.href = "login.html";
    return;
  }

  try {
    // Tu backend espera token como query: ?token=...
    const response = await fetch(`${API_VERIFICAR}?token=${token}`);

    if (!response.ok) {
      localStorage.clear();
      window.location.href = "login.html";
      return;
    }

    const data = await response.json();

    // Normalizar
    if (data.nombre) localStorage.setItem("nombre", data.nombre);
    if (data.rol)    localStorage.setItem("rol", data.rol.toLowerCase());

    // Mostrar nombre si hay contenedor
    const elementoNombre = document.getElementById("nombreUsuario");
    if (elementoNombre) {
      elementoNombre.textContent = nombreGuardado || data.nombre || "Usuario";
    }

    // Intentar renovar token en segundo plano
    await refreshToken();

    return data;

  } catch (error) {
    console.error("❌ Error en validarSesion()", error);
    localStorage.clear();
    window.location.href = "login.html";
  }
}

// ------------------------------------------------------------
// 🔁 REFRESH TOKEN AUTOMÁTICO (usa Authorization: Bearer)
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
// ⏱️ AUTO-REFRESH CADA N MINUTOS
// ------------------------------------------------------------
function iniciarAutoRefreshSesion(intervaloMinutos = 20) {
  if (refreshIntervalId !== null) return;

  refreshIntervalId = setInterval(() => {
    refreshToken();
  }, intervaloMinutos * 60 * 1000);
}

// ------------------------------------------------------------
// 🛡️ PROTEGER PÁGINA SEGÚN ROL
// ------------------------------------------------------------
function protegerPagina(rolesPermitidos) {
  const rol = (localStorage.getItem("rol") || "").toLowerCase();

  if (!rolesPermitidos.includes(rol)) {
    alert("Acceso no autorizado");
    window.location.href = "index.html";
  }
}

// ============================================================
// 🧠 HELPERS PARA FASE 6: fetchSeguro
// ============================================================

// Construye headers con Authorization automáticamente
function prepararHeaders(headers = {}) {
  const token = localStorage.getItem("token");
  const base = { ...headers };

  if (token) {
    base["Authorization"] = `Bearer ${token}`;
  }

  return base;
}

/**
 * fetchSeguro:
 *  - agrega Authorization automáticamente
 *  - si recibe 401, intenta refresh y reintenta una vez
 *  - si sigue 401, limpia sesión y manda a login
 *  - si recibe 403, muestra mensaje de permisos
 *  - retorna SIEMPRE el Response (no hace .json() internamente)
 */
async function fetchSeguro(url, options = {}, reintento = true) {
  const token = localStorage.getItem("token");

  if (!token) {
    // Sin token → sesión no válida
    window.location.href = "login.html";
    throw new Error("Sesión no válida (sin token)");
  }

  const opts = {
    ...options,
    headers: prepararHeaders(options.headers || {})
  };

  let response = await fetch(url, opts);

  // 401 → Intentamos refresh UNA sola vez y reintentar
  if (response.status === 401 && reintento) {
    await refreshToken();
    const nuevoToken = localStorage.getItem("token");

    if (!nuevoToken) {
      localStorage.clear();
      window.location.href = "login.html";
      throw new Error("Sesión expirada después de intentar refresh");
    }

    const optsRetry = {
      ...options,
      headers: prepararHeaders(options.headers || {})
    };

    response = await fetch(url, optsRetry);
  }

  // Si sigue 401 → matar sesión
  if (response.status === 401) {
    localStorage.clear();
    window.location.href = "login.html";
    throw new Error("Sesión expirada");
  }

  // 403 → sin permisos
  if (response.status === 403) {
    alert("❌ No tienes permisos para realizar esta acción.");
    throw new Error("Acceso denegado (403)");
  }

  return response;
}
