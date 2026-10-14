<template>
  <div class="test-module">
    <p class="test-module-intro">
      Describa cronológicamente las acciones realizadas desde el conocimiento del hecho hasta la puesta a disposición.
      <span>La narrativa se guarda en el servidor; los datos complementarios se guardan localmente para pruebas.</span>
    </p>

    <p v-if="errorCarga" class="test-module-error" role="alert">{{ errorCarga }}</p>
    <p v-if="errorGuardado" class="test-module-error" role="alert">{{ errorGuardado }}</p>
    <p v-if="guardado" class="test-module-success" role="status">{{ guardado }}</p>

    <form class="test-module-form" @submit.prevent="guardar">
      <section class="test-module-section">
        <header class="test-module-section-heading">
          <h2>Apartado 5.1 Descripción de los hechos y actuación de la autoridad</h2>
          <span>{{ form.narrativa.length }}/2507</span>
        </header>
        <div class="test-module-form-body">
          <label for="narrativa-iph">Narrativa de los hechos *</label>
          <textarea
            id="narrativa-iph"
            v-model="form.narrativa"
            rows="12"
            maxlength="2507"
            required
            placeholder="Escriba aquí la narración de los hechos y la actuación del primer respondiente..."
          />
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading">
          <h2>Datos del primer respondiente que realizó la narración</h2>
        </header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field">
            <span>Primer apellido</span>
            <input v-model="datos.primer_apellido" />
          </label>
          <label class="test-module-field">
            <span>Segundo apellido</span>
            <input v-model="datos.segundo_apellido" />
          </label>
          <label class="test-module-field">
            <span>Nombre(s)</span>
            <input v-model="datos.nombres" />
          </label>
          <label class="test-module-field">
            <span>Adscripción</span>
            <input v-model="datos.adscripcion" />
          </label>
          <label class="test-module-field">
            <span>Cargo / grado</span>
            <input v-model="datos.cargo" />
          </label>
          <label class="test-module-check test-module-signature">
            <input v-model="datos.firmo" type="checkbox" />
            Firma
          </label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading">
          <h2>Bien jurídico · Tipo de delito · Subtipo de delito</h2>
        </header>
        <div class="test-module-form-body">
          <div class="test-module-grid">
            <label class="test-module-field">
              <span>Bien jurídico</span>
              <input v-model="bienActual.bien_juridico" />
            </label>
            <label class="test-module-field">
              <span>Tipo de delito</span>
              <input v-model="bienActual.tipo_delito" />
            </label>
            <label class="test-module-field">
              <span>Subtipo de delito</span>
              <input v-model="bienActual.subtipo_delito" />
            </label>
            <label class="test-module-field test-module-field-wide">
              <span>Especifique subtipo de delito</span>
              <textarea v-model="bienActual.especifica" rows="2" />
            </label>
          </div>
          <div class="test-module-actions">
            <button type="button" class="test-module-secondary" @click="agregarBien">Agregar delito</button>
          </div>

          <div v-if="bienes.length" class="test-module-table-wrap">
            <table class="test-module-table">
              <thead>
                <tr><th>Bien jurídico</th><th>Tipo de delito</th><th>Subtipo</th><th>Especificación</th><th></th></tr>
              </thead>
              <tbody>
                <tr v-for="(bien, index) in bienes" :key="bien.id">
                  <td>{{ bien.bien_juridico }}</td>
                  <td>{{ bien.tipo_delito }}</td>
                  <td>{{ bien.subtipo_delito }}</td>
                  <td>{{ bien.especifica }}</td>
                  <td><button type="button" class="test-module-remove" @click="eliminarBien(index)">Eliminar</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <div class="test-module-actions test-module-footer">
        <button type="submit" class="test-module-primary" :disabled="guardando">
          {{ guardando ? "Guardando..." : "Guardar sección" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);
const guardando = ref(false);
const errorCarga = ref("");
const errorGuardado = ref("");
const guardado = ref("");
const form = ref({ narrativa: "" });
const datos = ref({
  primer_apellido: "",
  segundo_apellido: "",
  nombres: "",
  adscripcion: "",
  cargo: "",
  firmo: false,
});
const bienes = ref([]);
const bienActual = ref({
  bien_juridico: "",
  tipo_delito: "",
  subtipo_delito: "",
  especifica: "",
});
const storageKey = `iph-pruebas:${props.iphId}:seccion-5`;

async function cargar() {
  errorCarga.value = "";
  try {
    const { data } = await api.get(`/iph/${props.iphId}/narracion_primer_respondiente`);
    form.value.narrativa = data?.narrativa ?? data?.NARRATIVA ?? data?.descripcion ?? data?.DESCRIPCION ?? "";
  } catch (error) {
    console.error("No se pudo cargar la narrativa de la sección 5:", error);
    errorCarga.value = error.response?.data?.msg || "No se pudo cargar la narrativa guardada en el servidor.";
  }

  try {
    const guardados = localStorage.getItem(storageKey);
    if (!guardados) return;
    const extra = JSON.parse(guardados);
    if (!extra || typeof extra !== "object" || !Array.isArray(extra.bienes)) {
      throw new Error("Los datos complementarios no tienen el formato esperado.");
    }
    datos.value = { ...datos.value, ...extra.datos };
    bienes.value = extra.bienes;
  } catch (error) {
    console.error("No se pudieron cargar los datos complementarios de prueba:", error);
    errorCarga.value = "La narrativa se cargó, pero no se pudieron leer los datos complementarios guardados en este navegador.";
  }
}

function agregarBien() {
  if (!Object.values(bienActual.value).some((valor) => String(valor).trim())) return;
  bienes.value.push({ ...bienActual.value, id: `${Date.now()}-${Math.random()}` });
  bienActual.value = { bien_juridico: "", tipo_delito: "", subtipo_delito: "", especifica: "" };
}

function eliminarBien(indice) {
  bienes.value.splice(indice, 1);
}

async function guardar() {
  guardando.value = true;
  errorGuardado.value = "";
  guardado.value = "";
  try {
    await api.put(`/iph/${props.iphId}/narracion_primer_respondiente`, {
      narrativa: form.value.narrativa,
    });

    try {
      localStorage.setItem(storageKey, JSON.stringify({ datos: datos.value, bienes: bienes.value }));
    } catch (error) {
      console.error("No se pudieron guardar los datos complementarios de prueba:", error);
      errorGuardado.value = "La narrativa se guardó en el servidor, pero no fue posible guardar los datos complementarios en este navegador.";
      emit("guardado");
      return;
    }
    guardado.value = "Se guardó la narrativa y los datos complementarios de prueba.";
    emit("guardado");
  } catch (error) {
    console.error("No se pudo guardar la narrativa de la sección 5:", error);
    errorGuardado.value = error.response?.data?.msg || "No se pudo guardar la narrativa.";
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
