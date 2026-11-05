<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>
    <form ref="formulario" class="test-module-form" @submit.prevent="guardar">
      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>ANEXO F. ENTREGA - RECEPCIÓN DEL LUGAR DE LA INTERVENCIÓN</h2><span>Campo obligatorio*</span></header>
        <header class="test-module-section-heading"><h2>Apartado F.1 Preservación del lugar de la intervención</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-field"><span>Explique brevemente las acciones realizadas para la preservación del lugar de la intervención (delimitación, acordonamiento, cierre de calles, etc.)</span><textarea v-model="form.acciones_preservacion" rows="3" placeholder="EXPLIQUE BREVEMENTE LAS ACCIONES REALIZADAS PARA LA PRESERVACIÓN DEL LUGAR" /></label>
          <div class="test-module-grid annex-f-grid">
            <label class="test-module-field"><span>¿Solicitó apoyo de alguna autoridad o servicios especializados en el lugar de la intervención?</span><select v-model="form.solicito_apoyo"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><textarea v-model="form.apoyo_cual" :disabled="form.solicito_apoyo !== 'SÍ'" rows="2" placeholder="¿CUÁL?" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado F.2 Acciones realizadas después de la preservación</h2></header>
        <div class="test-module-form-body">
          <div class="test-module-grid annex-f-grid">
            <label class="test-module-field"><span>Después de la preservación del lugar de la intervención, ¿ingresó alguna persona al lugar?</span><select v-model="form.ingreso_persona"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>Motivo del ingreso</span><textarea v-model="form.motivo_ingreso" :disabled="form.ingreso_persona !== 'SÍ'" rows="2" placeholder="MOTIVO DEL INGRESO" /></label>
          </div>
          <p class="annex-instruction">Datos del personal que ingresó al lugar de la intervención.</p>
          <label class="test-module-check annex-check"><input v-model="seleccionarSeccion1" type="checkbox" @change="copiarRespondiente" /> Seleccione Primer Respondiente de la Sección 1</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="persona.primer_apellido" placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="persona.segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="persona.nombres" placeholder="NOMBRE(S)" /></label>
            <label class="test-module-field"><span>Institución</span><input v-model="persona.institucion" placeholder="INSTITUCIÓN" /></label>
            <label class="test-module-field"><span>Cargo / Grado</span><input v-model="persona.cargo" placeholder="CARGO/GRADO" /></label>
          </div>
          <div class="test-module-actions"><button type="button" class="test-module-secondary" @click="agregarPersonal">Agregar</button></div>
          <div class="test-module-table-wrap"><table class="test-module-table">
            <thead><tr><th>Primer apellido</th><th>Segundo apellido</th><th>Nombre(s)</th><th>Institución</th><th>Cargo/Grado</th><th>Eliminar</th></tr></thead>
            <tbody><tr v-if="!personal.length"><td colspan="6">No hay registros</td></tr><tr v-for="item in personal" :key="item.id"><td>{{ item.primer_apellido }}</td><td>{{ item.segundo_apellido }}</td><td>{{ item.nombres }}</td><td>{{ item.institucion }}</td><td>{{ item.cargo }}</td><td><button type="button" class="test-module-remove" @click="eliminarPersonal(item.id)">Eliminar</button></td></tr></tbody>
          </table></div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado F.3 Entrega - recepción del lugar de la intervención</h2></header>
        <div class="test-module-form-body">
          <p class="annex-instruction">Datos de la persona que entrega el lugar de la intervención.</p>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="form.entrega_primer_apellido" required placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.entrega_segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="form.entrega_nombres" required placeholder="NOMBRE(S)" /></label>
            <label class="test-module-field"><span>Adscripción *</span><input v-model="form.entrega_adscripcion" required placeholder="ADSCRIPCIÓN" /></label>
            <label class="test-module-field"><span>Cargo *</span><input v-model="form.entrega_cargo" required placeholder="CARGO" /></label>
            <label class="test-module-check"><input v-model="form.entrega_firma" type="checkbox" /> Firma</label>
          </div>
          <p class="annex-instruction annex-spaced">Datos de la persona que recibe el lugar de la intervención.</p>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="form.recibe_primer_apellido" required placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.recibe_segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="form.recibe_nombres" required placeholder="NOMBRE(S)" /></label>
            <label class="test-module-field"><span>Adscripción *</span><input v-model="form.recibe_adscripcion" required placeholder="ADSCRIPCIÓN" /></label>
            <label class="test-module-field"><span>Cargo *</span><input v-model="form.recibe_cargo" required placeholder="CARGO" /></label>
            <label class="test-module-check"><input v-model="form.recibe_firma" type="checkbox" /> Firma</label>
            <label class="test-module-field test-module-field-wide"><span>Observaciones</span><textarea v-model="form.observaciones" rows="2" placeholder="OBSERVACIONES" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado F.4 Fecha y hora de la entrega - recepción del lugar de la intervención</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Fecha *</span><input v-model="form.fecha" type="date" required /></label>
          <label class="test-module-field"><span>Hora * (24 horas)</span><input v-model="form.hora" type="time" required /></label>
        </div>
      </section>

      <div class="test-module-actions test-module-footer">
        <button type="submit" class="test-module-primary" :disabled="guardando">{{ guardando ? "Guardando..." : "Guardar anexo" }}</button>
        <button type="button" class="test-module-next" aria-label="Guardar e ir a bitácora" @click="guardarYSiguiente">➜</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "siguiente"]);
const formulario = ref(null);
const form = ref(crearFormulario());
const personal = ref([]);
const persona = ref({ primer_apellido: "", segundo_apellido: "", nombres: "", institucion: "", cargo: "" });
const seleccionarSeccion1 = ref(false);
const guardando = ref(false);
const error = ref("");
const mensaje = ref("");

function crearFormulario() {
  return {
    acciones_preservacion: "", solicito_apoyo: "", apoyo_cual: "", ingreso_persona: "", motivo_ingreso: "",
    entrega_primer_apellido: "", entrega_segundo_apellido: "", entrega_nombres: "", entrega_adscripcion: "",
    entrega_cargo: "", entrega_firma: false, recibe_primer_apellido: "", recibe_segundo_apellido: "",
    recibe_nombres: "", recibe_adscripcion: "", recibe_cargo: "", recibe_firma: false, observaciones: "",
    fecha: "", hora: "",
  };
}

async function cargar() {
  try {
    const saved = await leerCaptura(props.iphId, "anexo_f", `iph-anexo-f:${props.iphId}`) || {};
    form.value = { ...crearFormulario(), ...saved.form };
    personal.value = Array.isArray(saved.personal) ? saved.personal : [];
  } catch (exception) {
    console.error("No se pudieron cargar los datos del Anexo F:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron leer los datos guardados del Anexo F en el servidor.";
  }
}

async function persistir() {
  await guardarCaptura(props.iphId, "anexo_f", { form: form.value, personal: personal.value });
}

async function agregarPersonal() {
  if (!persona.value.primer_apellido && !persona.value.nombres) {
    error.value = "Capture al menos el nombre o el primer apellido del personal que ingresó.";
    return;
  }
  personal.value.push({ ...persona.value, id: `${Date.now()}-${Math.random()}` });
  persona.value = { primer_apellido: "", segundo_apellido: "", nombres: "", institucion: "", cargo: "" };
  try {
    await persistir();
    error.value = "";
  } catch (exception) {
    console.error("No se pudo guardar el personal del Anexo F:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el personal registrado en el servidor.";
  }
}

async function eliminarPersonal(id) {
  personal.value = personal.value.filter((item) => item.id !== id);
  try {
    await persistir();
  } catch (exception) {
    console.error("No se pudo eliminar al personal del Anexo F:", exception);
    error.value = "No se pudo eliminar el registro del personal.";
  }
}

async function copiarRespondiente() {
  error.value = "";
  if (!seleccionarSeccion1.value) return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
    const primerRespondiente = data.find((item) => item.es_primer_respondiente) || data[0];
    if (!primerRespondiente) throw new Error("No hay primer respondiente capturado en la Sección 1.");
    persona.value = {
      primer_apellido: primerRespondiente.primer_apellido || primerRespondiente.paterno || "",
      segundo_apellido: primerRespondiente.segundo_apellido || primerRespondiente.materno || "",
      nombres: primerRespondiente.nombres || primerRespondiente.nombre || "",
      institucion: primerRespondiente.institucion_otra || primerRespondiente.institucion || "",
      cargo: primerRespondiente.grado_cargo || "",
    };
  } catch (exception) {
    console.error("No se pudo copiar el primer respondiente:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente.";
    seleccionarSeccion1.value = false;
  }
}

async function guardar() {
  guardando.value = true;
  error.value = "";
  try {
    await persistir();
    mensaje.value = "Anexo F guardado en el servidor.";
    emit("guardado");
  } catch (exception) {
    console.error("No se pudo guardar el Anexo F:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el Anexo F en el servidor.";
  } finally {
    guardando.value = false;
  }
}

async function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  await guardar();
  if (!error.value) emit("siguiente");
}

onMounted(cargar);
</script>
