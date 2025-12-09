// ============================================================
// 🔐 reset.js — Frontend de recuperación de contraseña
// Maneja los 3 pasos del proceso
// ============================================================

const API = "http://127.0.0.1:8000/auth";

/* ------------------------------
   Elementos del DOM
   ------------------------------ */
const email = document.getElementById("email");
const codigo = document.getElementById("codigo");
const newPass = document.getElementById("newPass");

const paso1 = document.getElementById("paso1");
const paso2 = document.getElementById("paso2");
const paso3 = document.getElementById("paso3");

const msg = document.getElementById("mensaje");

/* ------------------------------
   BLOQUE 1 — Solicitar código
   ------------------------------ */
document.getElementById("btnEnviarCodigo").addEventListener("click", async () => {
    const response = await fetch(`${API}/recuperar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.value })
    });

    const data = await response.json();
    msg.innerHTML = `<div class="alert alert-info">${data.mensaje}</div>`;

    paso1.classList.add("d-none");
    paso2.classList.remove("d-none");
});

/* ------------------------------
   BLOQUE 2 — Validar código
   ------------------------------ */
document.getElementById("btnValidarCodigo").addEventListener("click", async () => {
    const response = await fetch(`${API}/validar-codigo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: email.value,
            codigo: codigo.value
        })
    });

    const data = await response.json();
    msg.innerHTML = `<div class="alert alert-success">${data.mensaje}</div>`;

    paso2.classList.add("d-none");
    paso3.classList.remove("d-none");
});


/* ------------------------------
   BLOQUE 3 — Restablecer contraseña
   ------------------------------ */
document.getElementById("btnRestablecer").addEventListener("click", async () => {
    const response = await fetch(`${API}/restablecer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: email.value,
            password: newPass.value
        })
    });

    const data = await response.json();
    msg.innerHTML = `<div class="alert alert-success">${data.mensaje}</div>`;
});
