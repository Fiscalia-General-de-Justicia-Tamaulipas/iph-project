<template>
  <form ref="formulario" class="disposicion-form primer-respondiente-form" @submit.prevent="agregar">
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
          <select id="institucion" v-model="form.institucion" required>
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
        <button type="button" class="primer-respondiente-remove" @click="eliminar(policia.id)">Eliminar</button>
      </div>
    </div>

    <div class="disposicion-actions primer-respondiente-actions">
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
import { onMounted, ref } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar", "siguiente"]);

const instituciones = [
  { value: "guardia_nacional", label: "GN-GUARDIA NACIONAL" },
  { value: "policia_federal_ministerial", label: "FM-POLICÍA FEDERAL MINISTERIAL" },
  { value: "policia_ministerial", label: "ME-POLICÍA MINISTERIAL" },
  { value: "policia_mando_unico", label: "MU-POLICÍA MANDO ÚNICO" },
  { value: "policia_estatal", label: "PE-POLICÍA ESTATAL" },
  { value: "policia_municipal", label: "PM-POLICÍA MUNICIPAL" },
  { value: "otra", label: "OA-OTRA AUTORIDAD" },
];

const entidades = [
  "AGUASCALIENTES", "BAJA CALIFORNIA", "BAJA CALIFORNIA SUR", "CAMPECHE", "CHIAPAS",
  "CHIHUAHUA", "CIUDAD DE MÉXICO", "COAHUILA", "COLIMA", "DURANGO", "GUANAJUATO",
  "GUERRERO", "HIDALGO", "JALISCO", "MÉXICO", "MICHOACÁN", "MORELOS", "NAYARIT",
  "NUEVO LEÓN", "OAXACA", "PUEBLA", "QUERÉTARO", "QUINTANA ROO", "SAN LUIS POTOSÍ",
  "SINALOA", "SONORA", "TABASCO", "TAMAULIPAS", "TLAXCALA", "VERACRUZ", "YUCATÁN",
  "ZACATECAS",
];

const municipiosTamaulipas = [
  "ABASOLO", "ALDAMA", "ALTAMIRA", "ANTIGUO MORELOS", "BURGOS", "BUSTAMANTE",
  "CAMARGO", "CASAS", "CIUDAD MADERO", "CRUILLAS", "GÓMEZ FARÍAS", "GONZÁLEZ",
  "GÜÉMEZ", "GUERRERO", "GUSTAVO DÍAZ ORDAZ", "HIDALGO", "JAUMAVE", "JIMÉNEZ",
  "LLERA", "MAINERO", "EL MANTE", "MATAMOROS", "MÉNDEZ", "MIER", "MIGUEL ALEMÁN",
  "MIQUIHUANA", "NUEVO LAREDO", "NUEVO MORELOS", "OCAMPO", "PADILLA", "PALMILLAS",
  "REYNOSA", "RÍO BRAVO", "SAN CARLOS", "SAN FERNANDO", "SAN NICOLÁS",
  "SOTO LA MARINA", "TAMPICO", "TULA", "VALLE HERMOSO", "VICTORIA", "VILLAGRÁN",
  "XICOTÉNCATL",
];

function crearFormulario() {
  return {
    nombres: "",
    primer_apellido: "",
    segundo_apellido: "",
    grado_cargo: "",
    institucion: "",
    institucion_otra: "",
    unidad_arribo: "",
    entidad_federativa: "",
    municipio_adscripcion: "",
    no_aplica: false,
    arribo_multiple: "",
    cantidad_elementos: null,
  };
}

const lista = ref([]);
const guardando = ref(false);
const formulario = ref(null);
const seleccionarSeccion1 = ref(false);
const mensaje = ref("");
const error = ref("");
const form = ref(crearFormulario());

function cambiarEntidad() {
  if (form.value.entidad_federativa !== "TAMAULIPAS") {
    form.value.municipio_adscripcion = "";
  }
}

function etiquetaInstitucion(valor) {
  return instituciones.find((institucion) => institucion.value === valor)?.label || valor || "Sin institución";
}

function actualizarNoAplica() {
  if (form.value.no_aplica) form.value.unidad_arribo = "";
}

function copiarResponsableSeccion1() {
  mensaje.value = "";
  error.value = "";
  if (!seleccionarSeccion1.value) return;

  try {
    const borrador = localStorage.getItem(`iph-pruebas:${props.iphId}:puesta_disposicion`);
    const responsable = borrador ? JSON.parse(borrador)?.responsable : null;
    if (!responsable) {
      seleccionarSeccion1.value = false;
      error.value = "No hay datos guardados de quien realiza la puesta a disposición en la Sección 1.";
      return;
    }

    form.value.primer_apellido = responsable.primer_apellido || "";
    form.value.segundo_apellido = responsable.segundo_apellido || "";
    form.value.nombres = responsable.nombres || "";
    form.value.grado_cargo = responsable.cargo || "";
    mensaje.value = "Se copiaron los datos disponibles de la Sección 1. Verifica la información restante.";
  } catch (exception) {
    seleccionarSeccion1.value = false;
    error.value = `No se pudieron leer los datos de la Sección 1: ${exception.message}`;
  }
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
  lista.value = Array.isArray(data) ? data : [];
}

async function agregar() {
  guardando.value = true;
  mensaje.value = "";
  error.value = "";

  try {
    const payload = {
      nombres: form.value.nombres,
      primer_apellido: form.value.primer_apellido,
      segundo_apellido: form.value.segundo_apellido,
      grado_cargo: form.value.grado_cargo,
      institucion: form.value.institucion,
      institucion_otra: form.value.institucion === "otra" ? form.value.institucion_otra : "",
      unidad_arribo: form.value.no_aplica ? "NO APLICA" : form.value.unidad_arribo,
      es_primer_respondiente: 1,
      id_tipo_actor: 5,
    };

    await api.post(`/iph/${props.iphId}/policias/lista`, payload);
    const datosNoPersistidos = form.value.entidad_federativa
      || form.value.municipio_adscripcion
      || form.value.arribo_multiple
      || form.value.cantidad_elementos;
    const datosAdscritos = {
      entidad_federativa: form.value.entidad_federativa,
      municipio_adscripcion: form.value.municipio_adscripcion,
      arribo_multiple: form.value.arribo_multiple,
      cantidad_elementos: form.value.cantidad_elementos,
    };
    await cargar();
    form.value = { ...crearFormulario(), ...datosAdscritos };
    seleccionarSeccion1.value = false;
    mensaje.value = datosNoPersistidos
      ? "El elemento se guardó, pero entidad, municipio y cantidad de elementos aún no se almacenan en el modelo actual."
      : "Elemento guardado correctamente.";
    emit("guardado");
    return true;
  } catch (exception) {
    error.value = exception.response?.data?.msg || "No se pudo guardar el primer respondiente.";
    return false;
  } finally {
    guardando.value = false;
  }
}

async function siguiente() {
  const tieneDatos = form.value.nombres || form.value.primer_apellido || form.value.segundo_apellido
    || form.value.institucion || form.value.grado_cargo || form.value.unidad_arribo;
  if (tieneDatos) {
    if (!formulario.value?.reportValidity()) return;
    if (!await agregar()) return;
  }
  emit("siguiente");
}

async function eliminar(id) {
  mensaje.value = "";
  error.value = "";
  try {
    await api.delete(`/iph/${props.iphId}/policias/lista/${id}`);
    await cargar();
    emit("guardado");
  } catch (exception) {
    error.value = exception.response?.data?.msg || "No se pudo eliminar el elemento.";
  }
}

onMounted(cargar);
</script>
