<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>
    <form ref="formulario" class="test-module-form" @submit.prevent="guardar">
      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>ANEXO B. INFORME DEL USO DE LA FUERZA</h2><span>Campo obligatorio*</span></header>
        <p class="annex-instruction annex-pad">Llene este Anexo sólo en caso de lesionados y/o fallecidos con motivo del uso de la fuerza.</p>
        <header class="test-module-section-heading"><h2>Apartado B.1 Niveles del uso de la fuerza</h2></header>
        <div class="test-module-form-body">
          <div class="force-grid">
            <div>
              <p class="annex-label">Indique cuántos:</p>
              <div class="force-counts">
                <span></span><strong>Autoridad</strong><strong>Persona</strong>
                <label>Lesionados *</label><input v-model.number="form.lesionados_autoridad" type="number" min="0" />
                <input v-model.number="form.lesionados_persona" type="number" min="0" aria-label="Personas lesionadas" />
                <label>Fallecidos *</label><input v-model.number="form.fallecidos_autoridad" type="number" min="0" />
                <input v-model.number="form.fallecidos_persona" type="number" min="0" aria-label="Personas fallecidas" />
              </div>
            </div>
            <fieldset class="force-levels">
              <legend>Seleccione según corresponda:</legend>
              <label v-for="nivel in niveles" :key="nivel"><span>{{ nivel }}</span><input v-model="form.niveles" type="checkbox" :value="nivel" /></label>
            </fieldset>
          </div>
          <label class="test-module-field annex-field-block"><span>Describa las conductas (resistencia activa y de alta peligrosidad) que motivaron el uso de la fuerza: *</span><textarea v-model="form.conductas" rows="3" required placeholder="DESCRIBA LAS CONDUCTAS (RESISTENCIA ACTIVA Y DE ALTA PELIGROSIDAD) QUE MOTIVARON EL USO DE LA FUERZA" /></label>
          <div class="force-medical">
            <label class="test-module-field"><span>¿Brindó o solicitó asistencia médica? *</span><select v-model="form.asistencia_medica" required><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>Explique</span><textarea v-model="form.explicacion" rows="3" placeholder="EXPLIQUE" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado B.2 Datos del primer respondiente que realizó el informe del uso de la fuerza</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-check annex-check"><input v-model="form.seleccionar_seccion1" type="checkbox" @change="copiarRespondiente" /> Seleccione Primer Respondiente de la Sección 1</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido</span><input v-model="respondiente.primer_apellido" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="respondiente.segundo_apellido" /></label>
            <label class="test-module-field"><span>Nombre(s)</span><input v-model="respondiente.nombres" /></label>
            <label class="test-module-field"><span>Firma</span><select v-model="respondiente.firma"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>Cargo</span><input v-model="respondiente.cargo" /></label>
          </div>
          <div class="test-module-actions"><button type="button" class="test-module-secondary" @click="agregarRespondiente">Agregar</button></div>
          <div class="test-module-table-wrap">
            <table class="test-module-table">
              <thead><tr><th>Primer apellido</th><th>Segundo apellido</th><th>Nombre(s)</th><th>Firma</th><th>Cargo</th><th>Eliminar</th></tr></thead>
              <tbody>
                <tr v-if="!respondientes.length"><td colspan="6">No hay registros</td></tr>
                <tr v-for="(persona, index) in respondientes" :key="persona.id"><td>{{ persona.primer_apellido }}</td><td>{{ persona.segundo_apellido }}</td><td>{{ persona.nombres }}</td><td>{{ persona.firma }}</td><td>{{ persona.cargo }}</td><td><button type="button" class="test-module-remove" @click="eliminarRespondiente(index)">Eliminar</button></td></tr>
              </tbody>
            </table>
          </div>
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

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "siguiente"]);
const formulario = ref(null);
const niveles = ["Reducción física de movimientos", "Utilización de armas incapacitantes menos letales", "Utilización de armas de fuego o fuerza letal"];
const form = ref({
  lesionados_autoridad: 0, lesionados_persona: 0, fallecidos_autoridad: 0, fallecidos_persona: 0,
  niveles: [], conductas: "", asistencia_medica: "", explicacion: "", seleccionar_seccion1: false,
});
const respondiente = ref({ primer_apellido: "", segundo_apellido: "", nombres: "", firma: "", cargo: "" });
const respondientes = ref([]);
const guardando = ref(false);
const error = ref("");
const mensaje = ref("");

async function cargar() {
  try {
    const saved = await leerCaptura(props.iphId, "anexo_b", `iph-anexo-b:${props.iphId}`) || {};
    form.value = { ...form.value, ...saved.form };
    respondientes.value = Array.isArray(saved.respondientes) ? saved.respondientes : [];
  } catch (exception) {
    console.error("No se pudieron leer los datos del Anexo B:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron leer los datos guardados del Anexo B en el servidor.";
  }
}

async function persistir() {
  await guardarCaptura(props.iphId, "anexo_b", { form: form.value, respondientes: respondientes.value });
}

function agregarRespondiente() {
  if (!Object.values(respondiente.value).some((value) => String(value).trim())) return;
  respondientes.value.push({ ...respondiente.value, id: `${Date.now()}-${Math.random()}` });
  respondiente.value = { primer_apellido: "", segundo_apellido: "", nombres: "", firma: "", cargo: "" };
}

function eliminarRespondiente(index) {
  respondientes.value.splice(index, 1);
}

async function copiarRespondiente() {
  error.value = "";
  if (!form.value.seleccionar_seccion1) return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
    const persona = data.find((item) => item.es_primer_respondiente) || data[0];
    if (!persona) throw new Error("No hay primer respondiente capturado en la Sección 1.");
    respondiente.value = {
      primer_apellido: persona.primer_apellido || persona.paterno || "",
      segundo_apellido: persona.segundo_apellido || persona.materno || "",
      nombres: persona.nombres || persona.nombre || "",
      firma: "SÍ",
      cargo: persona.grado_cargo || "",
    };
    agregarRespondiente();
  } catch (exception) {
    console.error("No se pudo seleccionar al primer respondiente de la Sección 1:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente de la Sección 1.";
    form.value.seleccionar_seccion1 = false;
  }
}

async function guardar() {
  guardando.value = true;
  error.value = "";
  mensaje.value = "";
  try {
    await persistir();
    mensaje.value = "Anexo B guardado en el servidor.";
    emit("guardado");
  } catch (exception) {
    console.error("No se pudo guardar el Anexo B:", exception);
    error.value = exception.response?.data?.msg || "No fue posible guardar el Anexo B en el servidor.";
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
