<template>
  <form ref="formulario" class="disposicion-form" @submit.prevent="guardar">
    <section class="disposicion-block" aria-labelledby="anexos-titulo">
      <h2 id="anexos-titulo">Apartado 1.1 Fecha y hora de la puesta a disposición</h2>
      <div class="disposicion-metadata">
        <div>
          <label for="disposicion-fecha">Fecha *</label>
          <input id="disposicion-fecha" v-model="form.fecha" type="date" required />
        </div>
        <div>
          <label for="disposicion-hora">Hora * <span>(24 horas)</span></label>
          <input id="disposicion-hora" v-model="form.hora" type="time" required />
        </div>
        <div>
          <label for="disposicion-expediente">No. expediente</label>
          <input id="disposicion-expediente" v-model="form.no_expediente" type="text" maxlength="80" />
        </div>
      </div>
      <Transition name="annex-assistant" @after-enter="enfocarAnexoActual">
        <section v-if="!form.sin_anexos && anexoActual" :key="anexoActual.clave" class="disposicion-annex-assistant" aria-live="polite">
          <p class="disposicion-annex-progress">Anexo {{ indiceAnexoActual + 1 }} de {{ anexos.length }}</p>
          <h3>{{ anexoActual.nombre }}</h3>
          <fieldset class="disposicion-annex-answer">
            <legend>¿Se entrega este anexo?</legend>
            <label><input :id="`anexo-${anexoActual.clave}-si`" v-model="form.anexos[anexoActual.clave].entregado" type="radio" value="SI" required @change="enfocarCantidad" /> Sí</label>
            <label><input v-model="form.anexos[anexoActual.clave].entregado" type="radio" value="NO" required @change="continuarAnexo" /> No</label>
          </fieldset>
          <div v-if="form.anexos[anexoActual.clave].entregado === 'SI'" class="disposicion-annex-quantity">
            <label :for="`cantidad-${anexoActual.clave}`">Cantidad *</label>
            <input :id="`cantidad-${anexoActual.clave}`" ref="campoCantidad" v-model.number="form.anexos[anexoActual.clave].cantidad" type="number" min="1" required />
            <button type="button" class="disposicion-save-button" @click="continuarAnexo">Continuar</button>
          </div>
        </section>
      </Transition>
      <div class="disposicion-annex-chips" aria-label="Anexos respondidos">
        <button v-for="item in anexosRespondidos" :key="item.clave" type="button" class="disposicion-annex-chip" @click="editarAnexo(item.clave)">{{ item.clave }} · {{ item.nombre }}: {{ item.entregado === 'SI' ? `SÍ (${item.cantidad})` : 'NO' }}</button>
      </div>
      <p v-if="!anexoActual && !form.sin_anexos" class="disposicion-annex-summary" aria-live="polite">Anexos A–G respondidos. Continúa con la documentación complementaria.</p>

      <label class="disposicion-check disposicion-no-annexes">
        <input v-model="form.sin_anexos" type="checkbox" @change="actualizarAnexos" />
        No se entregan Anexos
      </label>

      <div v-if="!anexoActual" class="disposicion-docs">
        <label for="documentacion-complementaria">¿Anexa documentación complementaria? *</label>
        <select id="documentacion-complementaria" v-model="form.documentacion_complementaria">
          <option value="NO">NO</option>
          <option value="SI">SI</option>
        </select>
        <fieldset :disabled="form.documentacion_complementaria !== 'SI'">
          <legend>Seleccione el tipo de documentación</legend>
          <label v-for="documento in tiposDocumentacion" :key="documento" class="disposicion-check">
            <input v-model="form.tipos_documentacion" type="checkbox" :value="documento" />
            {{ documento }}
            <input v-if="documento === 'Otra' && form.tipos_documentacion.includes('Otra')" v-model="form.tipo_documentacion_otra" type="text" maxlength="120" aria-label="¿Cuál?" placeholder="¿Cuál?" />
          </label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block" aria-labelledby="entrega-titulo">
      <h2 id="entrega-titulo">Datos de quien realiza la puesta a disposición</h2>
      <div class="disposicion-person-grid">
        <div>
          <label for="responsable-apellido1">Primer apellido *</label>
          <input id="responsable-apellido1" v-model="form.responsable.primer_apellido" required maxlength="100" />
        </div>
        <div>
          <label for="responsable-apellido2">Segundo apellido</label>
          <input id="responsable-apellido2" v-model="form.responsable.segundo_apellido" maxlength="100" />
        </div>
        <div>
          <label for="responsable-nombres">Nombre(s) *</label>
          <input id="responsable-nombres" v-model="form.responsable.nombres" required maxlength="150" />
        </div>
        <div class="disposicion-wide">
          <label for="responsable-adscripcion">Adscripción *</label>
          <input id="responsable-adscripcion" v-model="form.responsable.adscripcion" required maxlength="200" />
        </div>
        <div class="disposicion-wide">
          <label for="responsable-cargo">Cargo/Grado *</label>
          <select id="responsable-cargo" v-model="form.responsable.cargo" required>
            <option value="Policía investigadora">Policía investigadora</option>
          </select>
        </div>
        <fieldset class="disposicion-radio-group">
          <legend>Firma *</legend>
          <label><input v-model="form.responsable.firma" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.responsable.firma" type="radio" value="NO" /> No</label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block" aria-labelledby="receptor-titulo">
      <h2 id="receptor-titulo">Fiscal/Autoridad que recibe la puesta a disposición</h2>
      <div class="disposicion-person-grid">
        <div>
          <label for="receptor-apellido1">Primer apellido *</label>
          <input id="receptor-apellido1" v-model="form.receptor.primer_apellido" required maxlength="100" />
        </div>
        <div>
          <label for="receptor-apellido2">Segundo apellido</label>
          <input id="receptor-apellido2" v-model="form.receptor.segundo_apellido" maxlength="100" />
        </div>
        <div>
          <label for="receptor-nombres">Nombre(s) *</label>
          <input id="receptor-nombres" v-model="form.receptor.nombres" required maxlength="150" />
        </div>
        <div class="disposicion-wide">
          <label for="receptor-institucion">Fiscalía/Autoridad *</label>
          <select id="receptor-institucion" v-model="form.receptor.institucion" required>
            <option value="Fiscalía General de Justicia">Fiscalía General de Justicia</option>
          </select>
        </div>
        <div class="disposicion-wide">
          <label for="receptor-adscripcion">Adscripción *</label>
          <input id="receptor-adscripcion" v-model="form.receptor.adscripcion" required maxlength="200" />
        </div>
        <div class="disposicion-wide">
          <label for="receptor-cargo">Cargo *</label>
          <select id="receptor-cargo" v-model="form.receptor.cargo" required>
            <option value="Policía Investigadora">Policía Investigadora</option>
          </select>
        </div>
        <fieldset class="disposicion-radio-group">
          <legend>Firma *</legend>
          <label><input v-model="form.receptor.firma" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.receptor.firma" type="radio" value="NO" /> No</label>
        </fieldset>
        <fieldset class="disposicion-radio-group">
          <legend>Sello de la institución/autoridad que recibe el formato IPH *</legend>
          <label><input v-model="form.receptor.sello" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.receptor.sello" type="radio" value="NO" /> No</label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block disposicion-upload" aria-labelledby="archivo-titulo">
      <h2 id="archivo-titulo">Formato IPH</h2>
      <p>
        Primero debe guardar avances. Después puede cargar el documento escaneado del IPH presentado
        ante el MP, firmado y sellado. Tamaño máximo: 50 MB.
      </p>
      <div class="disposicion-file-controls">
        <button
          type="button"
          class="disposicion-save-button"
          :disabled="!avancesGuardados"
          @click="selectorArchivo?.click()"
        >
          CARGAR ARCHIVO
        </button>
        <input
          ref="selectorArchivo"
          class="disposicion-file-input"
          type="file"
          hidden
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.mp3,.mp4,.mpeg,.mpg,.wav"
          aria-label="Seleccionar archivo del formato IPH"
          @change="agregarArchivo"
        />
      </div>
      <p v-if="errorArchivo" class="disposicion-error" role="alert">{{ errorArchivo }}</p>
      <table class="disposicion-file-table">
        <thead>
          <tr><th>Archivo</th><th>Tipo Archivo</th><th>Eliminar</th><th>Descargar</th></tr>
        </thead>
        <tbody>
          <tr v-for="archivo in archivos" :key="archivo.id">
            <td>{{ archivo.name }}</td>
            <td>{{ archivo.type || extension(archivo.name) }}</td>
            <td><button type="button" class="disposicion-text-button" @click="eliminarArchivo(archivo.id)">Eliminar</button></td>
            <td><button type="button" class="disposicion-text-button" @click="descargarArchivo(archivo)">Descargar</button></td>
          </tr>
          <tr v-if="!archivos.length"><td colspan="4">No se han cargado archivos para este IPH.</td></tr>
        </tbody>
      </table>
    </section>

    <p class="disposicion-test-note">
      Los avances y archivos se guardan en el servidor y quedan asociados a este IPH.
    </p>
    <p v-if="mensaje" class="disposicion-success" role="status">{{ mensaje }}</p>
    <p v-if="errorGuardado" class="disposicion-error" role="alert">{{ errorGuardado }}</p>

    <footer class="disposicion-actions">
      <button type="submit" class="disposicion-save-button">GUARDAR AVANCES</button>
      <button type="button" class="disposicion-next-button" aria-label="Guardar avances y continuar a la sección 2" @click="guardarYSiguiente">
        <span aria-hidden="true">➜</span>
      </button>
    </footer>
  </form>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { leerCaptura, guardarCaptura } from "../../store/capturas";
import { eliminarAdjunto, guardarAdjunto, listarAdjuntos, obtenerAdjunto } from "../../store/attachments";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  iph: { type: Object, default: null },
});
const emit = defineEmits(["guardado", "siguiente", "anexos-actualizados"]);

const anexos = [
  { clave: "A", nombre: "Anexo A. Detención(es)", obligatorio: true },
  { clave: "B", nombre: "Anexo B. Informe del uso de la fuerza", obligatorio: true },
  { clave: "C", nombre: "Anexo C. Inspección de vehículo", obligatorio: true },
  { clave: "D", nombre: "Anexo D. Inventario de armas y objetos", obligatorio: true },
  { clave: "E", nombre: "Anexo E. Entrevistas", obligatorio: true },
  { clave: "F", nombre: "Anexo F. Entrega-recepción del lugar de intervención", obligatorio: true },
  { clave: "G", nombre: "Anexo G. Continuación de narrativa", obligatorio: true },
];
const tiposDocumentacion = ["Fotografías", "Videos", "Audio", "Certificados médicos", "Otra"];
const campoCantidad = ref(null);
const indiceAnexoActual = computed(() => anexos.findIndex(({ clave }) => !form.value.anexos[clave].respondido));
const anexoActual = computed(() => anexos[indiceAnexoActual.value] || null);
const anexosRespondidos = computed(() => anexos.filter(({ clave }) => form.value.anexos[clave].respondido).map(({ clave, nombre }) => ({ ...form.value.anexos[clave], clave, nombre: nombre.replace(/^Anexo [A-G]\. /, "") })));
const formulario = ref(null);
const selectorArchivo = ref(null);
const archivos = ref([]);
const avancesGuardados = ref(false);
const errorArchivo = ref("");
const errorGuardado = ref("");
const mensaje = ref("");

function crearBorrador() {
  return {
    fecha: "",
    hora: "",
    no_expediente: props.iph?.no_expediente || "",
    sin_anexos: false,
    anexos: {
      A: { entregado: "", cantidad: 0, respondido: false },
      B: { entregado: "", cantidad: 0, respondido: false },
      C: { entregado: "", cantidad: 0, respondido: false },
      D: { entregado: "", cantidad: 0, respondido: false },
      E: { entregado: "", cantidad: 0, respondido: false },
      F: { entregado: "", cantidad: 0, respondido: false },
      G: { entregado: "", cantidad: 0, respondido: false },
    },
    documentacion_complementaria: "NO",
    tipos_documentacion: [],
    tipo_documentacion_otra: "",
    responsable: {
      primer_apellido: "",
      segundo_apellido: "",
      nombres: "",
      adscripcion: "",
      cargo: "Policía investigadora",
      firma: "",
    },
    receptor: {
      primer_apellido: "",
      segundo_apellido: "",
      nombres: "",
      institucion: "Fiscalía General de Justicia",
      adscripcion: "",
      cargo: "Policía Investigadora",
      firma: "",
      sello: "",
    },
  };
}

const form = ref(crearBorrador());
const claveBorrador = () => `iph-pruebas:${props.iphId}:puesta_disposicion`;

function notificarAnexos() {
  const entregados = Object.fromEntries(
    anexos.map(({ clave }) => [clave, !form.value.sin_anexos && form.value.anexos[clave].entregado === "SI"]),
  );
  emit("anexos-actualizados", entregados);
}

function limpiarAnexo(anexo) {
  form.value.anexos[anexo.clave].entregado = "NO";
  form.value.anexos[anexo.clave].cantidad = 0;
  form.value.anexos[anexo.clave].respondido = true;
}

function normalizarCadena() {
  for (const { clave } of anexos) {
    const dato = form.value.anexos[clave];
    dato.respondido = dato.respondido ?? Boolean(dato.entregado);
    dato.cantidad = dato.cantidad ?? (Number(dato.armas || 0) + Number(dato.objetos || 0));
    if (dato.entregado === "SI" && Number(dato.cantidad) < 1) dato.cantidad = 1;
  }
}

async function cargarBorrador() {
  errorGuardado.value = "";
  try {
    const datos = await leerCaptura(props.iphId, "puesta_disposicion", claveBorrador());
    if (datos == null) {
      form.value = crearBorrador();
      avancesGuardados.value = false;
      notificarAnexos();
      archivos.value = await listarAdjuntos(props.iphId, "puesta_disposicion");
      return;
    }
    if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
      throw new Error("El borrador guardado no tiene un formato válido.");
    }
    const base = crearBorrador();
    form.value = {
      ...base,
      ...datos,
      anexos: { ...base.anexos, ...(datos.anexos || {}) },
      responsable: { ...base.responsable, ...(datos.responsable || {}) },
      receptor: { ...base.receptor, ...(datos.receptor || {}) },
    };
    normalizarCadena();
    avancesGuardados.value = true;
    notificarAnexos();
  } catch (error) {
    avancesGuardados.value = false;
    errorGuardado.value = error.response?.data?.msg || `No se pudo cargar la captura del servidor: ${error.message}`;
  }
  try { archivos.value = await listarAdjuntos(props.iphId, "puesta_disposicion"); }
  catch (error) { errorArchivo.value = error.response?.data?.msg || "No se pudieron cargar los archivos del servidor."; }
}

async function guardar() {
  errorGuardado.value = "";
  mensaje.value = "";
  try {
    await guardarCaptura(props.iphId, "puesta_disposicion", form.value);
    avancesGuardados.value = true;
    mensaje.value = "Avances guardados en el servidor.";
    emit("guardado");
    return true;
  } catch (error) {
    avancesGuardados.value = false;
    errorGuardado.value = error.response?.data?.msg || `No se pudieron guardar los avances: ${error.message}`;
    return false;
  }
}

async function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  if (!form.value.sin_anexos && anexos.some(({ clave }) => !form.value.anexos[clave].respondido)) {
    errorGuardado.value = "Responde todos los anexos antes de avanzar.";
    return;
  }
  if (form.value.documentacion_complementaria === "SI" && form.value.tipos_documentacion.includes("Otra") && !form.value.tipo_documentacion_otra.trim()) {
    errorGuardado.value = "Indica cuál es la documentación complementaria seleccionada como Otra.";
    return;
  }
  if (await guardar()) emit("siguiente");
}

function actualizarAnexos() {
  if (form.value.sin_anexos) for (const anexo of anexos) limpiarAnexo(anexo);
  else for (const { clave } of anexos) form.value.anexos[clave].respondido = false;
  notificarAnexos();
}

async function enfocarCantidad() {
  await nextTick();
  campoCantidad.value?.focus();
}

function enfocarAnexoActual() {
  if (anexoActual.value) document.getElementById(`anexo-${anexoActual.value.clave}-si`)?.focus();
}

function continuarAnexo() {
  const actual = anexoActual.value;
  if (!actual) return;
  const dato = form.value.anexos[actual.clave];
  if (dato.entregado === "SI" && (!Number.isInteger(Number(dato.cantidad)) || Number(dato.cantidad) < 1)) {
    campoCantidad.value?.focus();
    campoCantidad.value?.reportValidity();
    return;
  }
  if (!dato.entregado) return;
  if (dato.entregado === "NO") dato.cantidad = 0;
  dato.respondido = true;
  notificarAnexos();
}

async function editarAnexo(clave) {
  form.value.anexos[clave].respondido = false;
  await nextTick();
  enfocarAnexoActual();
}

async function agregarArchivo(event) {
  errorArchivo.value = "";
  const seleccionados = Array.from(event.target.files || []);
  for (const file of seleccionados) {
    if (file.size > 50 * 1024 * 1024) {
      errorArchivo.value = `${file.name} excede el tamaño máximo de 50 MB.`;
      continue;
    }
    try {
      const id = `${props.iphId}-P-${Date.now()}-${Math.random()}`;
      await guardarAdjunto({ id, iphId: props.iphId, anexo: "puesta_disposicion", file });
      archivos.value = await listarAdjuntos(props.iphId, "puesta_disposicion");
    } catch (error) {
      errorArchivo.value = error.response?.data?.msg || `No se pudo guardar ${file.name} en el servidor.`;
    }
  }
  event.target.value = "";
}

async function eliminarArchivo(id) {
  try {
    await eliminarAdjunto(id, props.iphId);
    archivos.value = await listarAdjuntos(props.iphId, "puesta_disposicion");
  } catch (error) { errorArchivo.value = error.response?.data?.msg || "No se pudo eliminar el archivo del servidor."; }
}

async function descargarArchivo(archivo) {
  try {
  const descargado = await obtenerAdjunto(archivo.id, props.iphId);
  const url = URL.createObjectURL(descargado.blob);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = archivo.name;
  enlace.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
  } catch (error) { errorArchivo.value = error.response?.data?.msg || "No se pudo descargar el archivo del servidor."; }
}

function extension(nombre) {
  return nombre.split(".").pop()?.toUpperCase() || "Archivo";
}

watch(() => props.iphId, cargarBorrador);
watch(() => props.iph?.no_expediente, (noExpediente) => {
  if (noExpediente && !form.value.no_expediente) form.value.no_expediente = noExpediente;
});
onMounted(cargarBorrador);
</script>
