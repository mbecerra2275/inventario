const API_URL = "http://127.0.0.1:8000/productos/";
const API_SUCURSALES = "http://127.0.0.1:8000/sucursales/";

let editando = false;
let idProductoEditando = null;
let sucursalesMap = {}; 

document.addEventListener("DOMContentLoaded", async () => {
  await cargarSucursales();  
  crearFormulario();
  cargarProductos();
});

// ---------- CARGAR SUCURSALES ----------
async function cargarSucursales() {
  try {
    const res = await fetch(API_SUCURSALES, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });
    if (!res.ok) throw new Error("Error al obtener sucursales");
    const sucursales = await res.json();
    sucursalesMap = {};
    sucursales.forEach(s => {
      sucursalesMap[s.id] = s.nombre || `Sucursal ${s.id}`;
    });
  } catch (err) {
    console.warn("⚠️ No se pudieron cargar las sucursales:", err);
  }
}

// ---------- FORMULARIO DINÁMICO ----------
async function crearFormulario() {
  const form = document.getElementById("form-producto");
  if (!form) return;

  try {
    const res = await fetch(API_URL + "schema", {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });

    const columnas = await res.json();
    form.innerHTML = "";

    const excluir = ["id", "fecha_creacion"];

    columnas.forEach(col => {
      if (excluir.includes(col.name)) return;

      // campo sucursal_id con <select>
      if (col.name === "sucursal_id") {
        const div = document.createElement("div");
        div.classList.add("col-md-4");
        div.innerHTML = `
          <label for="sucursal_id" class="form-label">Sucursal</label>
          <select class="form-select" id="sucursal_id" name="sucursal_id">
            <option value="">Seleccione sucursal...</option>
            ${Object.entries(sucursalesMap).map(([id, nombre]) => `<option value="${id}">${nombre}</option>`).join("")}
          </select>
        `;
        form.appendChild(div);
        return;
      }

      let tipo = "text";
      if (col.type.includes("INT")) tipo = "number";
      if (col.type.includes("FLOAT")) tipo = "number";
      if (col.type.includes("DATE")) tipo = "date";

      const div = document.createElement("div");
      div.classList.add("col-md-4");
      div.innerHTML = `
        <label for="${col.name}" class="form-label text-capitalize">${col.name.replace(/_/g, " ")}</label>
        <input type="${tipo}" class="form-control" id="${col.name}" name="${col.name}" ${tipo === "number" ? 'step="any"' : ""}>
      `;
      form.appendChild(div);
    });

    // botón guardar
    const divBoton = document.createElement("div");
    divBoton.classList.add("col-12", "text-end");
    divBoton.innerHTML = `
      <button type="submit" id="btn-guardar" class="btn btn-success mt-3">
        <i class="bi bi-save"></i> Guardar Producto
      </button>
    `;
    form.appendChild(divBoton);

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (editando) {
        await actualizarProducto();
      } else {
        await guardarProducto();
      }
    });

  } catch (error) {
    console.error("Error generando formulario:", error);
  }
}

// ---------- OBTENER DATOS DEL FORMULARIO ----------
function obtenerDatosFormulario() {
  const form = document.getElementById("form-producto");
  const datos = {};

  Array.from(form.elements).forEach(el => {
    if (!el.id) return;
    let valor = el.value.trim();

    if (valor === "") return;

    if (el.type === "number" || el.tagName === "SELECT") {
      valor = parseFloat(valor);
      if (isNaN(valor)) return;
    }

    datos[el.id] = valor;
  });

  return datos;
}

// ---------- GUARDAR NUEVO PRODUCTO ----------
async function guardarProducto() {
  const rol = localStorage.getItem("rol");
  if (rol === "sucursal") {
    alert("❌ No tienes permisos para crear productos.");
    return;
  }

  const producto = obtenerDatosFormulario();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify(producto)
    });
    if (!res.ok) throw new Error("Error al guardar producto");

    alert("✅ Producto guardado correctamente");
    resetFormulario();
    cargarProductos();

  } catch (error) {
    console.error("Error al guardar producto:", error);
    alert("❌ No se pudo guardar el producto");
  }
}

// ---------- CARGAR PRODUCTOS ----------
async function cargarProductos() {
  const tabla = document.getElementById("tabla-productos");
  if (!tabla) return;

  try {
    const [colsRes, prodRes] = await Promise.all([
      fetch(API_URL + "schema", {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      }),
      fetch(API_URL, {
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        }
      })
    ]);

    const columnas = await colsRes.json();
    const productos = await prodRes.json();

    const visibles = columnas.filter(c => !["fecha_creacion"].includes(c.name));
    tabla.innerHTML = "";

    if (!productos.length) {
      tabla.innerHTML = `<tr><td colspan="${visibles.length + 1}" class="text-center">No hay productos</td></tr>`;
      return;
    }

    productos.forEach(p => {
      const row = document.createElement("tr");

      visibles.forEach(c => {
        let valor = p[c.name];

        if (c.name === "sucursal_id") {
          valor = sucursalesMap[p[c.name]] || "—";
        }

        if (valor === null || valor === undefined || valor === "") valor = "—";

        if (c.name.includes("precio") || c.name.includes("costo")) {
          valor = valor !== "—" ? `$${Number(valor).toFixed(2)}` : "—";
        }

        if (c.name.includes("fecha")) {
          valor = valor !== "—" ? new Date(valor).toLocaleDateString() : "—";
        }

        row.innerHTML += `<td>${valor}</td>`;
      });

      row.innerHTML += `
        <td>
          <button class="btn btn-sm btn-warning me-1 btn-editar" onclick="cargarParaEditar(${p.id})">
            <i class="bi bi-pencil-square"></i>
          </button>
          <button class="btn btn-sm btn-danger btn-eliminar" onclick="eliminarProducto(${p.id})">
            <i class="bi bi-trash"></i>
          </button>
        </td>`;
      tabla.appendChild(row);
    });

  } catch (error) {
    console.error("Error al cargar productos:", error);
  }
}

// ---------- CARGAR PRODUCTO EN FORMULARIO ----------
async function cargarParaEditar(id) {
  const rol = localStorage.getItem("rol");
  if (rol !== "admin") {
    alert("❌ Solo el administrador puede editar productos.");
    return;
  }

  try {
    const res = await fetch(API_URL, {
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });
    const productos = await res.json();
    const producto = productos.find(p => p.id === id);
    if (!producto) return alert("❌ Producto no encontrado");

    for (const campo in producto) {
      const input = document.getElementById(campo);
      if (input) input.value = producto[campo] ?? "";
    }

    idProductoEditando = id;
    editando = true;

    const btn = document.getElementById("btn-guardar");
    btn.classList.remove("btn-success");
    btn.classList.add("btn-primary");
    btn.innerHTML = `<i class="bi bi-pencil-square"></i> Actualizar Producto`;

    window.scrollTo({ top: 0, behavior: "smooth" });

  } catch (error) {
    console.error("Error cargando producto:", error);
  }
}

// ---------- ACTUALIZAR PRODUCTO ----------
async function actualizarProducto() {
  const rol = localStorage.getItem("rol");
  if (rol !== "admin") {
    alert("❌ No tienes permisos para actualizar productos.");
    return;
  }

  const datos = obtenerDatosFormulario();

  try {
    const res = await fetch(API_URL + idProductoEditando, {
      method: "PUT",
      headers: { 
        "Content-Type": "application/json",
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify(datos)
    });
    if (!res.ok) throw new Error("Error al actualizar producto");

    alert("✅ Producto actualizado correctamente");
    resetFormulario();
    cargarProductos();

  } catch (error) {
    console.error("Error actualizando producto:", error);
    alert("❌ No se pudo actualizar el producto");
  }
}

// ---------- ELIMINAR PRODUCTO ----------
async function eliminarProducto(id) {
  const rol = localStorage.getItem("rol");
  if (rol !== "admin") {
    alert("❌ Solo el administrador puede eliminar productos.");
    return;
  }

  if (!confirm("¿Seguro que deseas eliminar este producto?")) return;

  try {
    const res = await fetch(API_URL + id, { 
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${localStorage.getItem("token")}`
      }
    });
    if (!res.ok) throw new Error("Error al eliminar producto");

    alert("🗑️ Producto eliminado correctamente");
    cargarProductos();

  } catch (error) {
    console.error("Error al eliminar producto:", error);
  }
}

// ---------- RESETEAR FORMULARIO ----------
function resetFormulario() {
  document.getElementById("form-producto").reset();
  editando = false;
  idProductoEditando = null;

  const btn = document.getElementById("btn-guardar");
  btn.classList.remove("btn-primary");
  btn.classList.add("btn-success");
  btn.innerHTML = `<i class="bi bi-save"></i> Guardar Producto`;
}
