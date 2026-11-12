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
      <section class="disposicion-annex-overview" aria-label="Respuestas de anexos" :aria-busy="cargandoAnexos">
        <div class="disposicion-annex-overview-header">
          <div>
            <h3>Anexos</h3>
            <p aria-live="polite">{{ cantidadRespondidos }} de 7 respondidos</p>
          </div>
          <button ref="botonAbrirAnexos" type="button" class="disposicion-annex-open" :disabled="cargandoAnexos" @click="abrirPantallaAnexos">
            {{ todosRespondidos ? "Editar anexos" : "Responder anexos" }}
          </button>
        </div>
        <TransitionGroup name="annex-overview-chip" tag="div" class="disposicion-annex-chips" aria-label="Respuestas actuales">
          <button
            v-for="item in anexosRespondidos"
            :key="item.clave"
            type="button"
            class="disposicion-annex-chip"
            :disabled="cargandoAnexos"
            @click="abrirAnexoDesdeChip(item.clave)"
          >
            {{ item.clave }} · {{ item.respuesta ? "Sí" : "No" }}
          </button>
        </TransitionGroup>
      </section>

      <AnexosPantalla
        :abierta="pantallaAnexosAbierta"
        :respuestas="respuestasAnexos"
        :sin-anexos="form.sin_anexos"
        :cambios-pendientes="respuestasAnexosModificadas"
        :elemento-disparador="botonAbrirAnexos"
        :indice-inicial="indiceInicialAnexo"
        @cerrar="pantallaAnexosAbierta = false"
        @actualizar-respuestas="actualizarRespuestasAnexos"
        @ningun-anexo="marcarSinAnexos"
        @editar-anexo="editarAnexoDesdePantalla"
      />

      <div v-if="form.sin_anexos || todosRespondidos" class="disposicion-docs">
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
import { computed, onMounted, ref, watch } from "vue";
import { leerCaptura, guardarCaptura } from "../../store/capturas";
import { eliminarAdjunto, guardarAdjunto, listarAdjuntos, obtenerAdjunto } from "../../store/attachments";
import AnexosPantalla from "./AnexosPantalla.vue";

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
const respuestasVacias = () => Object.fromEntries(anexos.map(({ clave }) => [clave, null]));
const respuestasAnexos = ref(respuestasVacias());
const anexosRespondidos = computed(() => anexos
  .filter(({ clave }) => respuestasAnexos.value[clave] !== null)
  .map(({ clave, nombre }) => ({ clave, nombre, respuesta: respuestasAnexos.value[clave] })));
const cantidadRespondidos = computed(() => anexosRespondidos.value.length);
const todosRespondidos = computed(() => cantidadRespondidos.value === anexos.length);
const pantallaAnexosAbierta = ref(false);
const botonAbrirAnexos = ref(null);
const indiceInicialAnexo = ref(0);
const respuestasGuardadas = ref(respuestasVacias());
const sinAnexosGuardado = ref(false);
const cargandoAnexos = ref(true);
const respuestasAnexosModificadas = computed(() => form.value.sin_anexos !== sinAnexosGuardado.value ||
  anexos.some(({ clave }) => respuestasAnexos.value[clave] !== respuestasGuardadas.value[clave]));
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
    anexos.map(({ clave }) => [clave, !form.value.sin_anexos && respuestasAnexos.value[clave] === true]),
  );
  emit("anexos-actualizados", entregados);
}

function hidratarRespuestas(anexosGuardados = {}) {
  respuestasAnexos.value = Object.fromEntries(anexos.map(({ clave }) => {
    if (form.value.sin_anexos) return [clave, false];
    const dato = anexosGuardados?.[clave] || {};
    const tieneRespuesta = dato.respondido !== false && ["SI", "NO"].includes(dato.entregado);
    return [clave, tieneRespuesta ? dato.entregado === "SI" : null];
  }));
}

function actualizarRespuestasAnexos(respuestas) {
  respuestasAnexos.value = Object.fromEntries(anexos.map(({ clave }) => [
    clave,
    respuestas?.[clave] === true ? true : respuestas?.[clave] === false ? false : null,
  ]));
  form.value.sin_anexos = false;
  notificarAnexos();
}

function marcarSinAnexos() {
  respuestasAnexos.value = Object.fromEntries(anexos.map(({ clave }) => [clave, false]));
  form.value.sin_anexos = true;
  notificarAnexos();
}

function marcarRespuestasGuardadas() {
  respuestasGuardadas.value = { ...respuestasAnexos.value };
  sinAnexosGuardado.value = form.value.sin_anexos;
}

function indicePrimeraRespuestaPendiente() {
  const index = anexos.findIndex(({ clave }) => respuestasAnexos.value[clave] === null);
  return index < 0 ? anexos.length : index;
}

function abrirPantallaAnexos() {
  indiceInicialAnexo.value = indicePrimeraRespuestaPendiente();
  pantallaAnexosAbierta.value = true;
}

function abrirAnexoDesdeChip(clave) {
  form.value.sin_anexos = false;
  indiceInicialAnexo.value = anexos.findIndex((anexo) => anexo.clave === clave);
  notificarAnexos();
  pantallaAnexosAbierta.value = true;
}

function editarAnexoDesdePantalla() {
  if (form.value.sin_anexos) {
    form.value.sin_anexos = false;
    notificarAnexos();
  }
}

function abrirAutomaticamenteUnaVez() {
  const claveVisita = `iph:${props.iphId}:anexos-pantalla-abierta`;
  try {
    if (sessionStorage.getItem(claveVisita)) return;
    sessionStorage.setItem(claveVisita, "1");
  } catch (error) {
    console.warn("No se pudo recordar la primera visita al asistente de anexos:", error);
  }
  indiceInicialAnexo.value = indicePrimeraRespuestaPendiente();
  pantallaAnexosAbierta.value = true;
}

function crearPayloadCaptura() {
  const anexosPayload = Object.fromEntries(anexos.map(({ clave }) => {
    const respuesta = form.value.sin_anexos ? false : respuestasAnexos.value[clave];
    const respondido = respuesta !== null;
    return [clave, {
      entregado: respondido ? (respuesta ? "SI" : "NO") : "",
      cantidad: respuesta === true ? 1 : 0,
      respondido,
    }];
  }));
  return { ...form.value, anexos: anexosPayload };
}

async function cargarBorrador() {
  errorGuardado.value = "";
  pantallaAnexosAbierta.value = false;
  cargandoAnexos.value = true;
  form.value = crearBorrador();
  respuestasAnexos.value = respuestasVacias();
  archivos.value = [];
  avancesGuardados.value = false;
  errorArchivo.value = "";
  mensaje.value = "";
  marcarRespuestasGuardadas();
  try {
    const datos = await leerCaptura(props.iphId, "puesta_disposicion", claveBorrador());
    if (datos == null) {
      avancesGuardados.value = false;
      notificarAnexos();
    } else if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
      throw new Error("El borrador guardado no tiene un formato válido.");
    } else {
      const { anexos: anexosGuardados = {}, ...datosFormulario } = datos;
      const base = crearBorrador();
      form.value = {
        ...base,
        ...datosFormulario,
        responsable: { ...base.responsable, ...(datos.responsable || {}) },
        receptor: { ...base.receptor, ...(datos.receptor || {}) },
      };
      hidratarRespuestas(anexosGuardados);
      marcarRespuestasGuardadas();
      avancesGuardados.value = true;
      notificarAnexos();
    }
  } catch (error) {
    avancesGuardados.value = false;
    errorGuardado.value = error.response?.data?.msg || `No se pudo cargar la captura del servidor: ${error.message}`;
  }
  try { archivos.value = await listarAdjuntos(props.iphId, "puesta_disposicion"); }
  catch (error) { errorArchivo.value = error.response?.data?.msg || "No se pudieron cargar los archivos del servidor."; }
  cargandoAnexos.value = false;
  abrirAutomaticamenteUnaVez();
}

async function guardar() {
  errorGuardado.value = "";
  mensaje.value = "";
  try {
    await guardarCaptura(props.iphId, "puesta_disposicion", crearPayloadCaptura());
    marcarRespuestasGuardadas();
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
  if (!form.value.sin_anexos && !todosRespondidos.value) {
    errorGuardado.value = "Responde todos los anexos antes de avanzar.";
    return;
  }
  if (form.value.documentacion_complementaria === "SI" && form.value.tipos_documentacion.includes("Otra") && !form.value.tipo_documentacion_otra.trim()) {
    errorGuardado.value = "Indica cuál es la documentación complementaria seleccionada como Otra.";
    return;
  }
  if (await guardar()) emit("siguiente");
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

<style scoped>
.disposicion-annex-progress-wrap {
  width: min(calc(100% - 2rem), 420px);
  margin: 0.6rem auto 0.45rem;
}

.disposicion-annex-progress-track {
  position: relative;
  height: 0.42rem;
  overflow: hidden;
  border-radius: 999px;
  background: #e7ece9;
}

.disposicion-annex-progress-track span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #24744d;
  transition: width 600ms cubic-bezier(.22, 1, .36, 1);
}

.disposicion-annex-progress-active {
  position: absolute;
  top: 50%;
  width: 0.7rem;
  height: 0.7rem;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #185f3b;
  box-shadow: 0 0 0 2px rgb(36 116 77 / 22%);
  transform: translate(-50%, -50%);
  animation: annex-progress-pulse 1.8s ease-in-out infinite;
  transition: left 600ms cubic-bezier(.22, 1, .36, 1);
}

.disposicion-annex-dots {
  display: flex;
  justify-content: space-between;
  margin: 0.35rem 0.05rem 0;
}

.disposicion-annex-dots span {
  width: 0.36rem;
  height: 0.36rem;
  border-radius: 50%;
  background: #d3dad6;
  transition: background-color 250ms ease, transform 250ms ease;
}

.disposicion-annex-dots span.is-done {
  transform: scale(1.12);
  background: #24744d;
}

.disposicion-annex-dots span.is-current {
  animation: annex-progress-pulse 1.8s ease-in-out infinite;
}

.disposicion-annex-assistant {
  box-sizing: border-box;
  width: min(calc(100% - 2rem), 420px);
  margin: 0.55rem auto 0.65rem;
  padding: 1rem 1.1rem;
  border: 1px solid #e0e8e3;
  border-radius: 1rem;
  background: linear-gradient(145deg, #fff 0%, #f8fbf9 100%);
  box-shadow: 0 0.55rem 1.5rem rgb(26 54 40 / 9%);
  text-align: center;
}

.disposicion-annex-progress {
  margin: 0 0 0.4rem;
  color: #64746b;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}

.disposicion-annex-assistant h3 {
  margin: 0 auto 0.55rem;
  color: #21382b;
  font-size: clamp(1rem, 2.8vw, 1.18rem);
  line-height: 1.35;
}

.disposicion-annex-question {
  margin: 0 0 0.55rem;
  color: #53645a;
  font-size: 0.78rem;
}

.disposicion-annex-answer {
  display: flex;
  justify-content: center;
  gap: 0.65rem;
}

.disposicion-annex-choice {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: inline-flex;
  min-width: min(8.5rem, 43%);
  min-height: 44px;
  align-items: center;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.55rem 1rem;
  border: 1px solid transparent;
  border-radius: 0.75rem;
  color: #fff;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 160ms ease, box-shadow 180ms ease;
}

.disposicion-annex-choice.is-yes {
  background: #26734d;
  box-shadow: 0 0.25rem 0.6rem rgb(38 115 77 / 18%);
}

.disposicion-annex-choice.is-no {
  background: #68756e;
  box-shadow: 0 0.25rem 0.6rem rgb(57 70 62 / 15%);
}

.disposicion-annex-choice:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0.4rem 0.9rem rgb(36 62 47 / 22%);
}

.disposicion-annex-choice:active:not(:disabled),
.disposicion-annex-choice.is-selected {
  transform: scale(0.95);
}

.disposicion-annex-choice.is-selected {
  border-color: #fff;
  box-shadow: 0 0 0 3px rgb(36 116 77 / 20%);
}

.disposicion-annex-choice:focus-visible,
.disposicion-annex-chip:focus-visible {
  outline: 2px solid #d88a19;
  outline-offset: 2px;
}

.disposicion-annex-choice:disabled {
  cursor: wait;
}

.disposicion-annex-choice-icon {
  display: inline-grid;
  width: 1.1rem;
  height: 1.1rem;
  flex: 0 0 1.1rem;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 70%);
  border-radius: 50%;
}

.disposicion-annex-choice-icon svg,
.disposicion-annex-finish-check svg {
  width: 75%;
  height: 75%;
  overflow: visible;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.5;
}

.disposicion-annex-choice-icon path {
  stroke-dasharray: 24;
  stroke-dashoffset: 24;
}

.disposicion-annex-choice.is-selected .disposicion-annex-choice-icon path {
  animation: annex-check-draw 190ms ease 35ms forwards;
}

.disposicion-annex-choice > span:not(.disposicion-annex-choice-icon):not(.disposicion-annex-ripple) {
  position: relative;
  z-index: 1;
}

.disposicion-annex-ripple {
  position: absolute;
  z-index: 0;
  top: var(--ripple-y);
  left: var(--ripple-x);
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: rgb(255 255 255 / 30%);
  pointer-events: none;
  transform: scale(0);
  animation: annex-ripple 460ms ease-out forwards;
}

.disposicion-annex-hint,
.disposicion-annex-finish-caption {
  margin: 0.55rem 0 0;
  color: #728078;
  font-size: 0.68rem;
}

.disposicion-annex-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
  box-sizing: border-box;
  width: min(calc(100% - 2rem), 420px);
  margin: 0 auto;
  padding: 0 0 0.6rem;
}

.disposicion-annex-chip {
  padding: 0.26rem 0.48rem;
  border: 1px solid #d5dfd9;
  border-radius: 999px;
  background: #f3f7f4;
  color: #34483b;
  font-size: 0.66rem;
  cursor: pointer;
  transition: transform 180ms ease, background-color 180ms ease;
}

.disposicion-annex-chip:disabled {
  cursor: default;
}

.disposicion-annex-finish {
  padding-top: 0.85rem;
  padding-bottom: 0.9rem;
}

.disposicion-annex-finish-check {
  display: inline-grid;
  width: 2.25rem;
  height: 2.25rem;
  place-items: center;
  border-radius: 50%;
  background: #e4f3e9;
  color: #24744d;
  animation: annex-finish-check 500ms cubic-bezier(.22, 1, .36, 1) both;
}

.disposicion-annex-finish-check path {
  stroke-dasharray: 24;
  stroke-dashoffset: 24;
  animation: annex-check-draw 300ms ease 160ms forwards;
}

.disposicion-annex-finish h3 {
  margin: 0.4rem 0 0;
}

.disposicion-annex-finish-caption {
  margin-top: 0.25rem;
}

.disposicion-annex-finish-list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.3rem;
  margin: 0.65rem 0 0;
  padding: 0;
  list-style: none;
}

.disposicion-annex-finish-list li {
  padding: 0.12rem;
  border: 1px solid #e0e8e3;
  border-radius: 999px;
  background: #fff;
}

.disposicion-annex-finish-list .disposicion-annex-chip {
  border: 0;
}

.annex-wizard-enter-active,
.annex-wizard-back-enter-active {
  transition: transform 500ms cubic-bezier(.22, 1, .36, 1), opacity 500ms ease, filter 500ms ease;
  will-change: transform, opacity, filter;
}

.annex-wizard-leave-active,
.annex-wizard-back-leave-active {
  transition: transform 220ms ease-in, opacity 220ms ease-in, filter 220ms ease-in;
  will-change: transform, opacity, filter;
}

.annex-wizard-leave-to {
  transform: translateX(-60px) scale(0.96);
  filter: blur(4px);
  opacity: 0;
}

.annex-wizard-enter-from {
  transform: translateX(60px) scale(0.96);
  filter: blur(6px);
  opacity: 0;
}

.annex-wizard-back-leave-to {
  transform: translateX(60px) scale(0.96);
  filter: blur(4px);
  opacity: 0;
}

.annex-wizard-back-enter-from {
  transform: translateX(-60px) scale(0.96);
  filter: blur(6px);
  opacity: 0;
}

.annex-wizard-enter-active .disposicion-annex-progress,
.annex-wizard-back-enter-active .disposicion-annex-progress {
  animation: annex-stagger-in 360ms cubic-bezier(.22, 1, .36, 1) 40ms both;
}

.annex-wizard-enter-active h3,
.annex-wizard-back-enter-active h3 {
  animation: annex-stagger-in 380ms cubic-bezier(.22, 1, .36, 1) 100ms both;
}

.annex-wizard-enter-active .disposicion-annex-choice:first-child,
.annex-wizard-back-enter-active .disposicion-annex-choice:first-child {
  animation: annex-stagger-in 380ms cubic-bezier(.22, 1, .36, 1) 160ms both;
}

.annex-wizard-enter-active .disposicion-annex-choice:nth-child(2),
.annex-wizard-back-enter-active .disposicion-annex-choice:nth-child(2) {
  animation: annex-stagger-in 380ms cubic-bezier(.22, 1, .36, 1) 220ms both;
}

.annex-wizard-enter-active .disposicion-annex-finish-check,
.annex-wizard-back-enter-active .disposicion-annex-finish-check {
  will-change: transform, opacity;
}

.annex-chip-enter-active,
.annex-chip-leave-active {
  transition: transform 260ms cubic-bezier(.22, 1, .36, 1), opacity 180ms ease;
  will-change: transform, opacity;
}

.annex-chip-enter-from,
.annex-chip-leave-to {
  transform: scale(0.8);
  opacity: 0;
}

.annex-chip-move {
  transition: transform 300ms cubic-bezier(.22, 1, .36, 1);
  will-change: transform;
}

.annex-summary-enter-active,
.annex-summary-leave-active {
  transition: transform 300ms cubic-bezier(.22, 1, .36, 1), opacity 220ms ease;
  will-change: transform, opacity;
}

.annex-summary-enter-from,
.annex-summary-leave-to {
  transform: scale(0.88);
  opacity: 0;
}

.annex-summary-move {
  transition: transform 300ms cubic-bezier(.22, 1, .36, 1);
  will-change: transform;
}

.annex-summary-enter-active {
  animation: annex-stagger-in 360ms cubic-bezier(.22, 1, .36, 1) var(--summary-delay, 0ms) both;
}

@keyframes annex-stagger-in {
  from { transform: translateY(7px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes annex-check-draw {
  to { stroke-dashoffset: 0; }
}

@keyframes annex-ripple {
  to { transform: scale(18); opacity: 0; }
}

@keyframes annex-finish-check {
  from { transform: scale(0.65); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

@keyframes annex-progress-pulse {
  50% { box-shadow: 0 0 0 5px rgb(36 116 77 / 12%); }
}

@media (max-width: 520px) {
  .disposicion-annex-assistant {
    padding: 0.85rem 0.7rem;
  }

  .disposicion-annex-choice {
    min-width: 0;
    min-height: 44px;
    flex: 1;
    padding: 0.5rem;
  }

  .disposicion-annex-progress-wrap,
  .disposicion-annex-chips {
    width: min(calc(100% - 1.3rem), 420px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .disposicion-annex-progress-track span,
  .disposicion-annex-dots span,
  .disposicion-annex-choice,
  .disposicion-annex-finish-check {
    transition: none;
    animation-duration: 0.01ms;
    animation-iteration-count: 1;
  }

  .disposicion-annex-finish-check path {
    animation: none;
    stroke-dashoffset: 0;
  }

  .disposicion-annex-choice.is-selected .disposicion-annex-choice-icon path {
    animation: none;
    stroke-dashoffset: 0;
  }

  .disposicion-annex-ripple {
    display: none;
  }

  .disposicion-annex-progress-active {
    transition: none;
  }

  .annex-wizard-enter-active,
  .annex-wizard-leave-active,
  .annex-wizard-back-enter-active,
  .annex-wizard-back-leave-active {
    transition: opacity 180ms ease;
    filter: none;
  }

  .annex-wizard-enter-from,
  .annex-wizard-leave-to,
  .annex-wizard-back-enter-from,
  .annex-wizard-back-leave-to {
    transform: none;
    filter: none;
  }

  .annex-wizard-enter-active .disposicion-annex-progress,
  .annex-wizard-back-enter-active .disposicion-annex-progress,
  .annex-wizard-enter-active h3,
  .annex-wizard-back-enter-active h3,
  .annex-wizard-enter-active .disposicion-annex-choice,
  .annex-wizard-back-enter-active .disposicion-annex-choice,
  .annex-summary-enter-active {
    animation: annex-reduced-fade 180ms ease both;
  }

  .annex-chip-enter-active,
  .annex-chip-leave-active,
  .annex-chip-move,
  .annex-summary-enter-active,
  .annex-summary-leave-active,
  .annex-summary-move {
    transition: opacity 160ms ease;
  }

  .annex-chip-enter-from,
  .annex-chip-leave-to,
  .annex-summary-enter-from,
  .annex-summary-leave-to {
    transform: none;
    opacity: 0;
  }

  .disposicion-annex-progress-active,
  .disposicion-annex-dots span.is-current {
    animation: none;
  }
}

@keyframes annex-reduced-fade {
  from { opacity: 0; }
  to { opacity: 1; }
}

.disposicion-annex-overview {
  margin: 0.6rem 0.7rem;
  padding: 0.6rem 0.7rem;
  border: 1px solid #dfe5e1;
  border-radius: 0.7rem;
  background: #fafcfb;
}

.disposicion-annex-overview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.disposicion-annex-overview-header h3 {
  margin: 0;
  color: #2f4037;
  font-size: 0.8rem;
}

.disposicion-annex-overview-header p {
  margin: 0.18rem 0 0;
  color: #758179;
  font-size: 0.68rem;
}

.disposicion-annex-open {
  min-height: 2.2rem;
  padding: 0.45rem 0.75rem;
  border: 1px solid #1e6b48;
  border-radius: 999px;
  background: #1e6b48;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  white-space: nowrap;
  cursor: pointer;
  transition: background-color 160ms ease, transform 160ms ease;
}

.disposicion-annex-open:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #15583a;
}

.disposicion-annex-open:disabled {
  opacity: 0.55;
  cursor: wait;
}

.disposicion-annex-overview .disposicion-annex-chips {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0;
}

.annex-overview-chip-enter-active,
.annex-overview-chip-leave-active {
  transition: transform 230ms cubic-bezier(.22, 1, .36, 1), opacity 180ms ease;
  will-change: transform, opacity;
}

.annex-overview-chip-enter-from,
.annex-overview-chip-leave-to {
  transform: scale(0.82);
  opacity: 0;
}

.annex-overview-chip-move {
  transition: transform 250ms cubic-bezier(.22, 1, .36, 1);
  will-change: transform;
}

@media (max-width: 520px) {
  .disposicion-annex-overview {
    margin: 0.55rem 0.5rem;
    padding: 0.55rem;
  }

  .disposicion-annex-overview-header {
    gap: 0.4rem;
  }

  .disposicion-annex-open {
    min-height: 2rem;
    padding: 0.4rem 0.6rem;
    font-size: 0.65rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .disposicion-annex-open {
    transition: none;
  }

  .annex-overview-chip-enter-active,
  .annex-overview-chip-leave-active,
  .annex-overview-chip-move {
    transition: opacity 160ms ease;
  }

  .annex-overview-chip-enter-from,
  .annex-overview-chip-leave-to {
    transform: none;
  }
}
</style>
