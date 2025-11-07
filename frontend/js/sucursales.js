const API_SUCURSALES = "http://127.0.0.1:8000/sucursales/";

let editando = false;
let idSucursalEditando = null;

document.addEventListener("DOMContentLoaded", () => {
  cargarSucursales();

  const form = document.getElementById("form-sucursal");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (editando) {
      await actualizarSucursal();
    } else {
      await crearSucursal();
    }
  });
});

// ---------- CREAR SUCURSAL ----------
async function crearSucursal() {
  const datos = obtenerDatosFormulario();
  try {
    const res = await fetch(API_SUCURSALES, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    if (!res.ok) throw new Error("Error al crear sucursal");

    alert("✅ Sucursal registrada correctamente");
    resetFormulario();
    cargarSucursales();
  } catch (err) {
    console.error(err);
    alert("❌ No se pudo registrar la sucursal");
  }
}

// ---------- OBTENER DATOS DEL FORMULARIO ----------
function obtenerDatosFormulario() {
  return {
    nombre: document.getElementById("nombre").value.trim(),
    direccion: document.getElementById("direccion").value.trim(),
    ciudad: document.getElementById("ciudad").value.trim(),
    telefono: document.getElementById("telefono").value.trim(),
    estado: document.getElementById("estado").value,
    encargado: document.getElementById("encargado").value.trim(),
  };
}

// ---------- LISTAR SUCURSALES ----------
async function cargarSucursales() {
  const tabla = document.getElementById("tabla-sucursales");
  try {
    const res = await fetch(API_SUCURSALES);
    if (!res.ok) throw new Error("Error al listar sucursales");
    const sucursales = await res.json();

    tabla.innerHTML = "";
    if (!sucursales.length) {
      tabla.innerHTML = `<tr><td colspan="9" class="text-center">No hay sucursales registradas</td></tr>`;
      return;
    }

    sucursales.forEach(s => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${s.id}</td>
        <td>${s.nombre}</td>
        <td>${s.direccion || "—"}</td>
        <td>${s.ciudad || "—"}</td>
        <td>${s.telefono || "—"}</td>
        <td>${s.encargado || "—"}</td>
        <td>
          <span class="badge ${s.estado === 'Activo' ? 'bg-success' : 'bg-secondary'}">
            ${s.estado || "—"}
          </span>
        </td>
        <td>${s.fecha_creacion ? new Date(s.fecha_creacion).toLocaleDateString() : "—"}</td>
        <td>
          <button class="btn btn-sm btn-warning me-1" onclick="cargarParaEditar(${s.id})">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn btn-sm btn-danger" onclick="eliminarSucursal(${s.id})">
            <i class="bi bi-trash"></i>
          </button>
        </td>
      `;
      tabla.appendChild(row);
    });
  } catch (err) {
    console.error(err);
  }
}

// ---------- CARGAR SUCURSAL PARA EDITAR ----------
async function cargarParaEditar(id) {
  try {
    const res = await fetch(API_SUCURSALES);
    const sucursales = await res.json();
    const sucursal = sucursales.find(s => s.id === id);
    if (!sucursal) return alert("Sucursal no encontrada");

    document.getElementById("nombre").value = sucursal.nombre || "";
    document.getElementById("direccion").value = sucursal.direccion || "";
    document.getElementById("ciudad").value = sucursal.ciudad || "";
    document.getElementById("telefono").value = sucursal.telefono || "";
    document.getElementById("estado").value = sucursal.estado || "Activo";
    document.getElementById("encargado").value = sucursal.encargado || "";

    idSucursalEditando = id;
    editando = true;

    const btn = document.getElementById("btn-guardar-sucursal");
    btn.classList.remove("btn-success");
    btn.classList.add("btn-primary");
    btn.innerHTML = `<i class="bi bi-pencil-square"></i> Actualizar Sucursal`;

    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    console.error(err);
  }
}

// ---------- ACTUALIZAR SUCURSAL ----------
async function actualizarSucursal() {
  const datos = obtenerDatosFormulario();
  try {
    const res = await fetch(API_SUCURSALES + idSucursalEditando, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos),
    });
    if (!res.ok) throw new Error("Error al actualizar sucursal");

    alert("✅ Sucursal actualizada correctamente");
    resetFormulario();
    cargarSucursales();
  } catch (err) {
    console.error(err);
    alert("❌ No se pudo actualizar la sucursal");
  }
}

// ---------- ELIMINAR SUCURSAL ----------
async function eliminarSucursal(id) {
  if (!confirm("¿Deseas eliminar esta sucursal?")) return;

  try {
    const res = await fetch(API_SUCURSALES + id, { method: "DELETE" });
    if (!res.ok) throw new Error("Error al eliminar sucursal");

    alert("🗑️ Sucursal eliminada correctamente");
    cargarSucursales();
  } catch (err) {
    console.error(err);
  }
}

// ---------- RESET FORMULARIO ----------
function resetFormulario() {
  document.getElementById("form-sucursal").reset();
  editando = false;
  idSucursalEditando = null;

  const btn = document.getElementById("btn-guardar-sucursal");
  btn.classList.remove("btn-primary");
  btn.classList.add("btn-success");
  btn.innerHTML = `<i class="bi bi-save"></i> Guardar Sucursal`;
}
