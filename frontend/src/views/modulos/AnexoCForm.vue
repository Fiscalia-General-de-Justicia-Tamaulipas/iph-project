<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>
    <form ref="formulario" class="test-module-form" @submit.prevent="guardarInspeccion">
      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>ANEXO C. INSPECCIÓN DE VEHÍCULO</h2><span>Campo obligatorio*</span></header>
        <div class="test-module-form-body annex-toolbar">
          <p class="annex-instruction">Llene este Anexo por cada vehículo inspeccionado.</p>
          <span class="annex-count">Vehículos inspeccionados: {{ vehiculos.length }}</span>
          <button type="button" class="test-module-secondary" @click="nuevoVehiculo">Nueva inspección</button>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado C.1 Fecha y hora de la inspección</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Fecha *</span><input v-model="form.fecha_inspeccion" type="date" required /></label>
          <label class="test-module-field"><span>Hora * (24 horas)</span><input v-model="form.hora_inspeccion" type="time" required /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado C.2 Datos generales del vehículo inspeccionado</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Tipo *</span><select v-model="form.tipo" required><option value="">- - - -</option><option>TERRESTRE</option><option>ACUÁTICO</option><option>AÉREO</option></select></label>
          <label class="test-module-field"><span>Procedencia</span><select v-model="form.procedencia"><option value="">- - - -</option><option>NACIONAL</option><option>EXTRANJERO</option></select></label>
          <label class="test-module-field"><span>Marca</span><input v-model="form.marca" placeholder="MARCA" /></label>
          <label class="test-module-field"><span>Modelo</span><input v-model="form.modelo" placeholder="MODELO" /></label>
          <label class="test-module-field"><span>Color</span><input v-model="form.color" placeholder="COLOR" /></label>
          <label class="test-module-field"><span>Uso</span><select v-model="form.uso"><option value="">- - - -</option><option>PARTICULAR</option><option>TRANSPORTE PÚBLICO</option><option>CARGA</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Placa / Matrícula</span><input v-model="form.placa_matricula" placeholder="PLACA/MATRÍCULA" /></label>
          <label class="test-module-field test-module-field-wide"><span>Número de serie</span><input v-model="form.no_serie" placeholder="NÚMERO DE SERIE" /></label>
          <label class="test-module-field test-module-field-wide"><span>Situación *</span><select v-model="form.situacion" required><option value="">- - - -</option><option>CON REPORTE DE ROBO</option><option>SIN REPORTE DE ROBO</option><option>NO ES POSIBLE SABERLO</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Observaciones</span><textarea v-model="form.observaciones" rows="3" placeholder="OBSERVACIONES" /></label>
          <label class="test-module-field test-module-field-wide"><span>Destino que se le dio</span><textarea v-model="form.disposicion" rows="2" placeholder="DESTINO" /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado C.3 Objetos encontrados en el vehículo inspeccionado</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-field annex-inline-field"><span>¿Encontró objetos relacionados con los hechos?</span><select v-model="form.encontro_objetos"><option value="">- - - -</option><option value="SI">SÍ</option><option value="NO">NO</option></select></label>
          <label v-if="form.encontro_objetos === 'SI'" class="test-module-field annex-field-block"><span>Describa los objetos encontrados</span><textarea v-model="form.objetos_descripcion" rows="3" placeholder="DESCRIPCIÓN DE LOS OBJETOS" /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado C.4 Datos del primer respondiente que realizó la inspección, sólo si es diferente a quien firmó la puesta a disposición</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-check annex-check"><input v-model="seleccionarSeccion1" type="checkbox" @change="copiarRespondiente" /> Seleccione Primer Respondiente de la Sección 1</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido</span><input v-model="respondiente.primer_apellido" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="respondiente.segundo_apellido" /></label>
            <label class="test-module-field"><span>Nombre(s)</span><input v-model="respondiente.nombres" /></label>
            <label class="test-module-field"><span>Adscripción</span><input v-model="respondiente.adscripcion" /></label>
            <label class="test-module-field"><span>Cargo / Grado</span><input v-model="respondiente.cargo" /></label>
            <label class="test-module-field"><span>Firma</span><select v-model="respondiente.firma"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
          </div>
          <div class="test-module-actions"><button type="button" class="test-module-secondary" @click="agregarRespondiente">Agregar</button></div>
          <div class="test-module-table-wrap">
            <table class="test-module-table">
              <thead><tr><th>Primer apellido</th><th>Segundo apellido</th><th>Nombre(s)</th><th>Adscripción</th><th>Cargo/Grado</th><th>Firma</th><th>Eliminar</th></tr></thead>
              <tbody>
                <tr v-if="!respondientes.length"><td colspan="7">No hay registros</td></tr>
                <tr v-for="(persona, index) in respondientes" :key="persona.id"><td>{{ persona.primer_apellido }}</td><td>{{ persona.segundo_apellido }}</td><td>{{ persona.nombres }}</td><td>{{ persona.adscripcion }}</td><td>{{ persona.cargo }}</td><td>{{ persona.firma }}</td><td><button type="button" class="test-module-remove" @click="eliminarRespondiente(index)">Eliminar</button></td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado C.5 Imágenes del vehículo inspeccionado</h2></header>
        <div class="test-module-form-body">
          <p class="annex-instruction">Primero debe “Guardar Anexo”; posteriormente podrá cargar imágenes JPG, JPEG o BMP de hasta 50 MB.</p>
          <div class="annex-upload">
            <input ref="archivoInput" type="file" accept=".jpg,.jpeg,.bmp,image/jpeg,image/bmp" :disabled="!vehiculos.length" @change="cargarImagen" />
            <button type="button" class="test-module-secondary" :disabled="!vehiculos.length || cargandoImagen" @click="archivoInput?.click()">{{ cargandoImagen ? "Cargando..." : "Cargar archivo" }}</button>
          </div>
          <ul v-if="imagenes.length" class="annex-file-list"><li v-for="imagen in imagenes" :key="imagen.id"><span>{{ imagen.name }}</span><button type="button" class="test-module-remove" @click="descargarImagen(imagen.id)">Descargar</button><button type="button" class="test-module-remove" @click="eliminarImagen(imagen.id)">Eliminar</button></li></ul>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Inspecciones registradas <span>{{ vehiculos.length }}</span></h2></header>
        <div class="test-module-table-wrap">
          <table class="test-module-table">
            <thead><tr><th>Tipo</th><th>Marca</th><th>Modelo</th><th>Placa/Matrícula</th><th>Fecha</th><th>Eliminar</th></tr></thead>
            <tbody>
              <tr v-if="!vehiculos.length"><td colspan="6">No hay registros</td></tr>
              <tr v-for="vehiculo in vehiculos" :key="vehiculo.id"><td>{{ vehiculo.tipo }}</td><td>{{ vehiculo.marca }}</td><td>{{ vehiculo.modelo }}</td><td>{{ vehiculo.placa_matricula }}</td><td>{{ vehiculo.fecha_inspeccion }}</td><td><button type="button" class="test-module-remove" @click="eliminarVehiculo(vehiculo.id)">Eliminar</button></td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <div class="test-module-actions test-module-footer">
        <button type="submit" class="test-module-primary" :disabled="guardando">{{ guardando ? "Guardando..." : "Guardar anexo" }}</button>
        <button type="button" class="test-module-next" aria-label="Guardar e ir al siguiente anexo" @click="guardarYSiguiente">➜</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";
import { eliminarAdjunto, guardarAdjunto, listarAdjuntos, obtenerAdjunto } from "../../store/attachments";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "siguiente"]);
const formulario = ref(null);
const form = ref(crearFormulario());
const vehiculos = ref([]);
const respondiente = ref({ primer_apellido: "", segundo_apellido: "", nombres: "", adscripcion: "", cargo: "", firma: "" });
const respondientes = ref([]);
const imagenes = ref([]);
const seleccionarSeccion1 = ref(false);
const guardando = ref(false);
const cargandoImagen = ref(false);
const archivoInput = ref(null);
const error = ref("");
const mensaje = ref("");

function crearFormulario() {
  return {
    fecha_inspeccion: "", hora_inspeccion: "", tipo: "", procedencia: "", uso: "", marca: "",
    modelo: "", color: "", placa_matricula: "", no_serie: "", situacion: "", observaciones: "",
    disposicion: "", encontro_objetos: "", objetos_descripcion: "",
  };
}

async function cargar() {
  error.value = "";
  try {
    const { data } = await api.get(`/iph/${props.iphId}/inspeccion_vehiculo/lista`);
    vehiculos.value = Array.isArray(data) ? data : [];
  } catch (exception) {
    console.error("No se pudieron cargar las inspecciones de vehículos:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron cargar los vehículos guardados.";
  }
  try {
    const saved = await leerCaptura(props.iphId, "anexo_c_complemento", `iph-anexo-c:${props.iphId}`) || {};
    respondientes.value = Array.isArray(saved.respondientes) ? saved.respondientes : [];
    imagenes.value = await listarAdjuntos(props.iphId, "C");
  } catch (exception) {
    console.error("No se pudieron cargar los datos complementarios del Anexo C:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron leer los datos complementarios del Anexo C en el servidor.";
  }
}

async function persistirComplementos() {
  await guardarCaptura(props.iphId, "anexo_c_complemento", { respondientes: respondientes.value });
}

async function agregarRespondiente() {
  if (!Object.values(respondiente.value).some((value) => String(value).trim())) return;
  respondientes.value.push({ ...respondiente.value, id: `${Date.now()}-${Math.random()}` });
  respondiente.value = { primer_apellido: "", segundo_apellido: "", nombres: "", adscripcion: "", cargo: "", firma: "" };
  try {
    await persistirComplementos();
  } catch (exception) {
    console.error("No se pudieron guardar los datos del primer respondiente del Anexo C:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el registro del primer respondiente en el servidor.";
  }
}

async function eliminarRespondiente(index) {
  respondientes.value.splice(index, 1);
  try { await persistirComplementos(); } catch (exception) { error.value = exception.response?.data?.msg || "No se pudo guardar el cambio en el servidor."; }
}

async function copiarRespondiente() {
  error.value = "";
  if (!seleccionarSeccion1.value) return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
    const persona = data.find((item) => item.es_primer_respondiente) || data[0];
    if (!persona) throw new Error("No hay primer respondiente capturado en la Sección 1.");
    respondiente.value = {
      primer_apellido: persona.primer_apellido || persona.paterno || "",
      segundo_apellido: persona.segundo_apellido || persona.materno || "",
      nombres: persona.nombres || persona.nombre || "",
      adscripcion: persona.institucion_otra || persona.institucion || "",
      cargo: persona.grado_cargo || "",
      firma: "SÍ",
    };
    await agregarRespondiente();
  } catch (exception) {
    console.error("No se pudo seleccionar al primer respondiente de la Sección 1:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente de la Sección 1.";
    seleccionarSeccion1.value = false;
  }
}

async function guardarInspeccion() {
  guardando.value = true;
  error.value = "";
  mensaje.value = "";
  try {
    const payload = {
      ...form.value,
      encontro_objetos: form.value.encontro_objetos === "SI" ? true : form.value.encontro_objetos === "NO" ? false : null,
      observaciones: [form.value.observaciones, form.value.objetos_descripcion ? `Objetos encontrados: ${form.value.objetos_descripcion}` : ""].filter(Boolean).join("\n"),
    };
    const { data } = await api.post(`/iph/${props.iphId}/inspeccion_vehiculo/lista`, payload);
    vehiculos.value.push(data);
    form.value = crearFormulario();
    mensaje.value = "Inspección de vehículo guardada.";
    emit("guardado");
    return true;
  } catch (exception) {
    console.error("No se pudo guardar la inspección del vehículo:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar la inspección del vehículo.";
    return false;
  } finally {
    guardando.value = false;
  }
}

async function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  const tieneCaptura = Object.values(form.value).some((valor) => valor !== "" && valor !== null);
  if (tieneCaptura && !(await guardarInspeccion())) return;
  try {
    await persistirComplementos();
    emit("siguiente");
  } catch (exception) {
    error.value = exception.response?.data?.msg || "No se pudieron guardar los datos complementarios del Anexo C.";
  }
}

function nuevoVehiculo() {
  form.value = crearFormulario();
  mensaje.value = "";
}

async function eliminarVehiculo(id) {
  try {
    await api.delete(`/iph/${props.iphId}/inspeccion_vehiculo/lista/${id}`);
    vehiculos.value = vehiculos.value.filter((vehiculo) => vehiculo.id !== id);
    emit("guardado");
  } catch (exception) {
    console.error("No se pudo eliminar la inspección del vehículo:", exception);
    error.value = exception.response?.data?.msg || "No se pudo eliminar la inspección del vehículo.";
  }
}

async function cargarImagen(event) {
  error.value = "";
  const file = event.target.files?.[0];
  if (!file) return;
  if (!/\.(jpe?g|bmp)$/i.test(file.name) || file.size > 50 * 1024 * 1024) {
    error.value = "Seleccione una imagen JPG, JPEG o BMP de hasta 50 MB.";
    event.target.value = "";
    return;
  }
  cargandoImagen.value = true;
  try {
    const id = `${props.iphId}-C-${Date.now()}-${Math.random()}`;
    await guardarAdjunto({ id, iphId: props.iphId, anexo: "C", file });
    imagenes.value = await listarAdjuntos(props.iphId, "C");
  } catch (exception) {
    console.error("No se pudo guardar el archivo del Anexo C:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el archivo del Anexo C en el servidor.";
  } finally {
    cargandoImagen.value = false;
    event.target.value = "";
  }
}

async function eliminarImagen(id) {
  try {
    await eliminarAdjunto(id);
    imagenes.value = await listarAdjuntos(props.iphId, "C");
  } catch (exception) {
    console.error("No se pudo eliminar el archivo del Anexo C:", exception);
    error.value = "No se pudo eliminar el archivo.";
  }
}

async function descargarImagen(id) {
  try {
    const archivo = await obtenerAdjunto(id);
    if (!archivo) throw new Error("Archivo no encontrado.");
    const url = URL.createObjectURL(archivo.blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = archivo.name;
    link.click();
    URL.revokeObjectURL(url);
  } catch (exception) {
    console.error("No se pudo descargar el archivo del Anexo C:", exception);
    error.value = "No se pudo descargar el archivo seleccionado.";
  }
}

onMounted(cargar);
</script>
