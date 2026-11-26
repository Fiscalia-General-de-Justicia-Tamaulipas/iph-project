<template>
  <div class="primer-respondiente-modo" role="group" aria-label="Modo de captura">
    <button
      type="button"
      :aria-pressed="!capturaGuiada"
      :class="{ activa: !capturaGuiada }"
      @click="capturaGuiada = false"
    >
      Formulario completo
    </button>
    <button
      type="button"
      :aria-pressed="capturaGuiada"
      :class="{ activa: capturaGuiada }"
      @click="capturaGuiada = true"
    >
      Captura guiada
    </button>
  </div>

  <div v-if="capturaGuiada" class="primer-respondiente-captura-guiada">
    <p v-if="mensaje" class="primer-respondiente-message" role="status">{{ mensaje }}</p>
    <CapturaGuiadaMotor
      :preguntas="preguntasGuiadas"
      :datos="form"
      :contexto="contextoGuiado"
      titulo="Sección 2: Primer respondiente"
      :resumen-items="resumenItems"
      :resumen-aviso="avisoResumen"
      :resumen-aviso-accion="avisoResumenAccion"
      :guardando="guardando"
      :error-guardado="error"
      @actualizar="actualizarCampo"
      @guardar="guardarCapturaGuiada"
      @revisar-formulario="capturaGuiada = false"
      @receptor="revisarAvisoResumen"
    />
  </div>

  <form v-else ref="formulario" class="disposicion-form primer-respondiente-form" @submit.prevent="guardarFormularioCompleto">
    <section class="disposicion-block" aria-labelledby="primer-respondiente-identificacion">
      <h2 id="primer-respondiente-identificacion">Apartado 2.1 Datos de identificación</h2>

      <label class="disposicion-check primer-respondiente-from-section">
        <input v-model="seleccionarSeccion1" type="checkbox" @change="copiarResponsableSeccion1" />
        Seleccione Primer Respondiente de la Sección 1
      </label>

      <div class="disposicion-person-grid">
        <div>
          <label for="primer-apellido">Primer Apellido *</label>
          <input id="primer-apellido" v-model="form.primer_apellido" required maxlength="100" />
        </div>
        <div>
          <label for="segundo-apellido">Segundo Apellido</label>
          <input id="segundo-apellido" v-model="form.segundo_apellido" maxlength="100" />
        </div>
        <div>
          <label for="nombres">Nombre(s) *</label>
          <input id="nombres" v-model="form.nombres" required maxlength="150" />
        </div>

        <p class="primer-respondiente-instructions primer-respondiente-wide">
          Seleccione la institución a la que pertenece, así como la entidad federativa o municipio de adscripción.
        </p>

        <div>
          <label for="institucion">Institución *</label>
          <select id="institucion" v-model="form.institucion" required @change="cambiarInstitucion">
            <option value="">-- SELECCIONE --</option>
            <option v-for="institucion in instituciones" :key="institucion.value" :value="institucion.value">
              {{ institucion.label }}
            </option>
          </select>
        </div>
        <div>
          <label for="entidad-federativa">Entidad federativa *</label>
          <select id="entidad-federativa" v-model="form.entidad_federativa" required @change="cambiarEntidad">
            <option value="">-- SELECCIONE --</option>
            <option v-for="entidad in entidades" :key="entidad" :value="entidad">{{ entidad }}</option>
          </select>
        </div>
        <div>
          <label for="municipio-adscripcion">Municipio de adscripción</label>
          <select id="municipio-adscripcion" v-model="form.municipio_adscripcion" :disabled="form.entidad_federativa !== 'TAMAULIPAS'">
            <option value="">-- SELECCIONE --</option>
            <option v-for="municipio in municipiosTamaulipas" :key="municipio" :value="municipio">
              {{ municipio }}
            </option>
          </select>
        </div>

        <div class="primer-respondiente-wide">
          <label for="institucion-otra">Otra autoridad</label>
          <input
            id="institucion-otra"
            v-model="form.institucion_otra"
            :disabled="form.institucion !== 'otra'"
            placeholder="OTRA AUTORIDAD"
            maxlength="150"
          />
        </div>

        <div class="primer-respondiente-wide">
          <label for="grado-cargo">¿Cuál es su cargo o grado? *</label>
          <input id="grado-cargo" v-model="form.grado_cargo" required maxlength="100" />
        </div>

        <div class="primer-respondiente-unit-row">
          <label for="unidad-arribo">¿En qué unidad arribó al lugar de la intervención?</label>
          <input
            id="unidad-arribo"
            v-model="form.unidad_arribo"
            :disabled="form.no_aplica"
            maxlength="100"
          />
          <label class="disposicion-check primer-respondiente-no-aplica">
            No aplica
            <input v-model="form.no_aplica" type="checkbox" @change="actualizarNoAplica" />
          </label>
        </div>

        <div class="primer-respondiente-multiple primer-respondiente-wide">
          <label for="arribo-multiple">¿Arribó más de un elemento al lugar de la intervención?</label>
          <select id="arribo-multiple" v-model="form.arribo_multiple">
            <option value="">-- SELECCIONE --</option>
            <option value="SI">SI</option>
            <option value="NO">NO</option>
          </select>
          <label v-if="form.arribo_multiple === 'SI'" for="cantidad-elementos">¿Cuántos?</label>
          <input
            v-if="form.arribo_multiple === 'SI'"
            id="cantidad-elementos"
            v-model.number="form.cantidad_elementos"
            type="number"
            min="2"
            max="999"
            required
          />
          <span v-if="form.arribo_multiple === 'SI'" class="primer-respondiente-example">(001, 002, ..., 010, ...)</span>
        </div>
      </div>
    </section>

    <p v-if="mensaje" class="primer-respondiente-message" role="status">{{ mensaje }}</p>
    <p v-if="error" class="primer-respondiente-error" role="alert">{{ error }}</p>

    <div v-if="lista.length" class="primer-respondiente-list">
      <h2>Elementos registrados ({{ lista.length }})</h2>
      <div v-for="policia in lista" :key="policia.id" class="primer-respondiente-list-row">
        <span>
          {{ policia.primer_apellido || policia.paterno }}
          {{ policia.segundo_apellido || policia.materno }}
          {{ policia.nombres || policia.nombre }}
          <small>{{ policia.grado_cargo || "Sin cargo" }} · {{ etiquetaInstitucion(policia.institucion) }}</small>
        </span>
        <button
          v-if="policia.es_primer_respondiente"
          type="button"
          class="primer-respondiente-edit"
          @click="seleccionarRegistro(policia)"
        >
          {{ String(form.registro_relacional_id) === String(policia.id) ? "En edición" : "Usar este registro" }}
        </button>
        <button type="button" class="primer-respondiente-remove" @click="eliminar(policia.id)">Eliminar</button>
      </div>
    </div>

    <div class="disposicion-actions primer-respondiente-actions">
      <button
        v-if="lista.length"
        type="button"
        class="primer-respondiente-edit"
        @click="prepararNuevoRegistro"
      >
        Agregar otro elemento
      </button>
      <button type="submit" class="disposicion-save-button" :disabled="guardando">
        {{ guardando ? "GUARDANDO..." : "GUARDAR SECCIÓN" }}
      </button>
      <button
        type="button"
        class="disposicion-next-button"
        aria-label="Ir a la siguiente sección"
        title="Siguiente sección"
        @click="siguiente"
      >
        →
      </button>
    </div>
  </form>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";
import { useAuthStore } from "../../store/auth";
import CapturaGuiadaMotor from "../../components/CapturaGuiadaMotor.vue";
import preguntasGuiadas from "./capturaGuiada/PoliciasPreguntas";
import {
  entidades,
  instituciones,
  municipiosTamaulipas,
} from "./capturaGuiada/PoliciasCatalogos";
import {
  cargarPolicias,
  combinarRegistroConCaptura,
  crearFormularioPolicias,
  datosParaCapturaPolicias,
  entidadDesdeAdscripcion,
  formularioDesdeRegistro,
  guardarPolicias,
  municipioDesdeAdscripcion,
  opcionesRegistrosPolicias,
  validarFormularioPolicias,
} from "./capturaGuiada/PoliciasPersistencia";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar", "siguiente"]);
const auth = useAuthStore();
const lista = ref([]);
const guardando = ref(false);
const formulario = ref(null);
const seleccionarSeccion1 = ref(false);
const mensaje = ref("");
const error = ref("");
const form = ref(crearFormularioPolicias());
const capturaGuiada = ref(false);
const listaCargada = ref(false);
const capturaOriginal = ref(null);
const registrosAmbiguos = ref([]);
const datosLegacyIncompletos = ref(false);
const crearNuevoRegistro = ref(false);

const resumenItems = computed(() => [
  { etiqueta: "Primer apellido", valor: form.value.primer_apellido || "Sin capturar" },
  { etiqueta: "Segundo apellido", valor: form.value.segundo_apellido || "No aplica" },
  { etiqueta: "Nombre(s)", valor: form.value.nombres || "Sin capturar" },
  { etiqueta: "Institución", valor: etiquetaInstitucion(form.value.institucion) },
  { etiqueta: "Entidad federativa", valor: form.value.entidad_federativa || "Sin capturar" },
  { etiqueta: "Municipio de adscripción", valor: form.value.municipio_adscripcion || "No aplica" },
  {
    etiqueta: "Otra autoridad",
    valor: form.value.institucion === "otra" ? form.value.institucion_otra || "Sin capturar" : "No aplica",
  },
  { etiqueta: "Cargo o grado", valor: form.value.grado_cargo || "Sin capturar" },
  { etiqueta: "Unidad de arribo", valor: form.value.no_aplica ? "No aplica" : form.value.unidad_arribo || "Sin capturar" },
  { etiqueta: "Más de un elemento", valor: form.value.arribo_multiple === "SI" ? "Sí" : form.value.arribo_multiple === "NO" ? "No" : "Sin capturar" },
  {
    etiqueta: "Cantidad de elementos",
    valor: form.value.arribo_multiple === "SI"
      ? form.value.cantidad_elementos || "Pendiente en formulario completo"
      : "No aplica",
  },
]);

const adscripcionSesion = computed(() =>
  String(auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || "").trim(),
);
const entidadSesion = computed(() => entidadDesdeAdscripcion(adscripcionSesion.value));
const municipioSesion = computed(() =>
  municipioDesdeAdscripcion(adscripcionSesion.value, entidadSesion.value),
);
const cargoSesion = computed(() =>
  String(auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "").trim(),
);
const contextoGuiado = computed(() => ({
  leerResponsableSeccion1,
  registrosAmbiguos: opcionesRegistrosPolicias(registrosAmbiguos.value),
  entidadSesion: entidadSesion.value,
  municipioSesion: municipioSesion.value,
  cargoSesion: cargoSesion.value,
}));
const avisoResumen = computed(() => {
  const avisos = [];
  if (datosLegacyIncompletos.value) {
    avisos.push("Este IPH no tenía guardados entidad, municipio ni datos de arribo; verifica y guarda esas respuestas.");
  }
  if (
    form.value.arribo_multiple === "SI"
    && (!Number.isInteger(Number(form.value.cantidad_elementos))
      || Number(form.value.cantidad_elementos) < 2
      || Number(form.value.cantidad_elementos) > 999)
  ) {
    avisos.push("Falta indicar cuántos elementos arribaron (de 2 a 999) en el formulario completo.");
  }
  return avisos.join(" ");
});
const avisoResumenAccion = computed(() =>
  form.value.arribo_multiple === "SI"
  && (!Number.isInteger(Number(form.value.cantidad_elementos))
    || Number(form.value.cantidad_elementos) < 2
    || Number(form.value.cantidad_elementos) > 999)
    ? "Completar en formulario completo"
    : "",
);

function cambiarEntidad() {
  if (form.value.entidad_federativa !== "TAMAULIPAS") {
    form.value.municipio_adscripcion = "";
  }
}

function cambiarInstitucion() {
  if (form.value.institucion !== "otra") form.value.institucion_otra = "";
}

function etiquetaInstitucion(valor) {
  return instituciones.find((institucion) => institucion.value === valor)?.label || valor || "Sin institución";
}

function actualizarNoAplica() {
  if (form.value.no_aplica) form.value.unidad_arribo = "";
}

async function leerResponsableSeccion1() {
  const borrador = await leerCaptura(
    props.iphId,
    "puesta_disposicion",
    `iph-pruebas:${props.iphId}:puesta_disposicion`,
  );
  const responsable = borrador?.responsable;
  if (!responsable) {
    throw new Error("No hay datos guardados de quien realiza la puesta a disposición en la Sección 1.");
  }
  return responsable;
}

async function copiarResponsableSeccion1() {
  mensaje.value = "";
  error.value = "";
  if (!seleccionarSeccion1.value) return;
  try {
    const responsable = await leerResponsableSeccion1();
    form.value.primer_apellido = responsable.primer_apellido || "";
    form.value.segundo_apellido = responsable.segundo_apellido || "";
    form.value.nombres = responsable.nombres || "";
    form.value.grado_cargo = responsable.cargo || "";
    mensaje.value = "Se copiaron los datos disponibles de la Sección 1. Verifica la información restante.";
  } catch (exception) {
    seleccionarSeccion1.value = false;
    error.value = exception.response?.data?.msg || exception.message
      || "No se pudieron leer los datos de la Sección 1.";
  }
}

function seleccionarRegistro(registro) {
  if (String(form.value.registro_relacional_id) === String(registro.id)) return;
  form.value = capturaOriginal.value
    ? combinarRegistroConCaptura(registro, capturaOriginal.value, { priorizarRegistro: true })
    : formularioDesdeRegistro(registro);
  form.value.registro_relacional_id = String(registro.id);
  crearNuevoRegistro.value = false;
  error.value = "";
}

function prepararNuevoRegistro() {
  form.value = crearFormularioPolicias();
  capturaOriginal.value = null;
  crearNuevoRegistro.value = true;
  seleccionarSeccion1.value = false;
  mensaje.value = "";
  error.value = "";
}

function actualizarCampo({ ruta, valor }) {
  if (ruta === "registro_relacional_id") {
    if (String(form.value.registro_relacional_id) === String(valor)) return;
    const registro = lista.value.find((item) => String(item.id) === String(valor));
    if (registro) seleccionarRegistro(registro);
    return;
  }
  form.value[ruta] = valor;
  if (ruta === "unidad_arribo") form.value.no_aplica = valor === "NO APLICA";
  if (ruta === "institucion" && valor !== "otra") form.value.institucion_otra = "";
  if (ruta === "entidad_federativa") cambiarEntidad();
}

async function guardarCapturaGuiada() {
  await guardarSeccion({ capturaGuiada: true });
}

async function cargar() {
  error.value = "";
  try {
    const resultado = await cargarPolicias(props.iphId);
    form.value = resultado.formulario;
    capturaOriginal.value = resultado.capturaOriginal;
    lista.value = resultado.registros;
    registrosAmbiguos.value = resultado.registrosAmbiguos;
    listaCargada.value = resultado.listaCargada;
    datosLegacyIncompletos.value = resultado.datosLegacyIncompletos;
    if (resultado.errorCarga) error.value = resultado.errorCarga;
  } catch (exception) {
    listaCargada.value = false;
    error.value = exception.response?.data?.msg
      || `No se pudo cargar la Sección 2: ${exception.message}`;
  }
}

async function guardarSeccion({ capturaGuiada: modoGuiado = false } = {}) {
  const validacion = validarFormularioPolicias(form.value, { capturaGuiada: modoGuiado });
  if (validacion) {
    error.value = validacion;
    return false;
  }

  guardando.value = true;
  mensaje.value = "";
  error.value = "";

  try {
    const resultado = await guardarPolicias(props.iphId, form.value, {
      registros: lista.value,
      registroId: form.value.registro_relacional_id,
      listaCargada: listaCargada.value,
      crearNuevo: crearNuevoRegistro.value,
    });
    if (resultado.registroId) form.value.registro_relacional_id = resultado.registroId;
    if (resultado.capturaGuardada) {
      capturaOriginal.value = datosParaCapturaPolicias(form.value);
      datosLegacyIncompletos.value = false;
    }
    if (resultado.registroGuardado) {
      const idGuardado = String(resultado.registroGuardado.id);
      const existente = lista.value.findIndex((item) => String(item.id) === idGuardado);
      if (existente >= 0) lista.value[existente] = resultado.registroGuardado;
      else lista.value.push(resultado.registroGuardado);
      listaCargada.value = true;
      const ambiguo = registrosAmbiguos.value.findIndex((item) => String(item.id) === idGuardado);
      if (ambiguo >= 0) registrosAmbiguos.value[ambiguo] = resultado.registroGuardado;
      crearNuevoRegistro.value = false;
    }

    const faltaCantidad = modoGuiado
      && form.value.arribo_multiple === "SI"
      && (!Number.isInteger(Number(form.value.cantidad_elementos)) || Number(form.value.cantidad_elementos) < 2);
    const completo = resultado.guardadoCompleto && !faltaCantidad;
    if (completo) {
      mensaje.value = resultado.mensaje;
      emit("guardado");
    } else if (resultado.guardadoCompleto) {
      mensaje.value = `${resultado.mensaje} Falta indicar la cantidad de elementos en el formulario completo.`;
    } else {
      error.value = resultado.mensaje;
    }
    return completo;
  } catch (exception) {
    error.value = exception.response?.data?.msg || `No se pudo guardar la Sección 2: ${exception.message}`;
    return false;
  } finally {
    guardando.value = false;
  }
}

function guardarFormularioCompleto() {
  if (!formulario.value?.reportValidity()) return;
  return guardarSeccion();
}

async function siguiente() {
  const tieneDatos = form.value.nombres || form.value.primer_apellido || form.value.segundo_apellido
    || form.value.institucion || form.value.grado_cargo || form.value.unidad_arribo;
  if (tieneDatos) {
    if (!formulario.value?.reportValidity()) return;
    if (!await guardarSeccion()) return;
  }
  emit("siguiente");
}

async function eliminar(id) {
  mensaje.value = "";
  error.value = "";
  try {
    await api.delete(`/iph/${props.iphId}/policias/lista/${id}`);
    lista.value = lista.value.filter((policia) => String(policia.id) !== String(id));
    if (String(form.value.registro_relacional_id) === String(id)) {
      form.value = crearFormularioPolicias();
      capturaOriginal.value = null;
      try {
        await guardarCaptura(props.iphId, "policias", datosParaCapturaPolicias(form.value));
        emit("guardado");
      } catch (exception) {
        error.value = exception.response?.data?.msg
          || `El registro se eliminó, pero no se pudo actualizar la captura JSON: ${exception.message}`;
      }
    } else {
      emit("guardado");
    }
  } catch (exception) {
    error.value = exception.response?.data?.msg || "No se pudo eliminar el elemento.";
  }
}

function revisarAvisoResumen() {
  capturaGuiada.value = false;
  nextTick(() => {
    document.getElementById("cantidad-elementos")?.scrollIntoView({ behavior: "smooth", block: "center" });
  });
}

onMounted(cargar);
watch(() => props.iphId, cargar);
</script>

<style scoped>
.primer-respondiente-modo {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin-bottom: 1rem;
}

.primer-respondiente-modo button {
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 1px solid #6b1d3f;
  border-radius: 8px;
  background: #fff;
  color: #6b1d3f;
  font-size: 0.78rem;
  font-weight: 800;
}

.primer-respondiente-modo button.activa {
  background: #6b1d3f;
  color: #fff;
}

.primer-respondiente-captura-guiada {
  display: grid;
  gap: 0.75rem;
}

.primer-respondiente-edit {
  min-height: 36px;
  padding: 0.4rem 0.65rem;
  border: 1px solid #6b1d3f;
  border-radius: 6px;
  background: #fff;
  color: #6b1d3f;
  font-size: 0.72rem;
  font-weight: 700;
}
</style>
