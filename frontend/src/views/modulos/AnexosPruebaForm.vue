<template>
  <div class="test-module">
    <div class="test-module-intro">
      <p>{{ configuracion.instruccion }}</p>
      <span>Modo de prueba · Los registros se conservan en este navegador</span>
    </div>

    <div v-if="error" class="test-module-error" role="alert">{{ error }}</div>

    <section class="test-module-section">
      <header class="test-module-section-heading">
        <h2>{{ configuracion.apartado }}</h2>
        <span>{{ registros.length }} {{ registros.length === 1 ? "registro" : "registros" }}</span>
      </header>

      <form class="test-module-form" @submit.prevent="agregarRegistro">
        <div class="test-module-grid">
          <div v-for="campo in configuracion.campos" :key="campo.key" class="test-module-field" :class="{ 'test-module-field-wide': campo.wide || campo.type === 'textarea' || campo.type === 'checks' }">
            <label :for="`${tipo}-${campo.key}`">{{ campo.label }}<span v-if="campo.required"> *</span></label>

            <textarea
              v-if="campo.type === 'textarea'"
              :id="`${tipo}-${campo.key}`"
              v-model="formulario[campo.key]"
              :rows="campo.rows || 3"
              :required="campo.required"
              :maxlength="campo.maxlength"
              :placeholder="campo.placeholder"
            />
            <select
              v-else-if="campo.type === 'select'"
              :id="`${tipo}-${campo.key}`"
              v-model="formulario[campo.key]"
              :required="campo.required"
            >
              <option value="">-- SELECCIONE --</option>
              <option v-for="opcion in campo.options" :key="opcion" :value="opcion">{{ opcion }}</option>
            </select>
            <div v-else-if="campo.type === 'checks'" class="test-module-checks">
              <label v-for="opcion in campo.options" :key="opcion" class="test-module-check">
                <input v-model="formulario[campo.key]" type="checkbox" :value="opcion" />
                {{ opcion }}
              </label>
            </div>
            <input
              v-else
              :id="`${tipo}-${campo.key}`"
              v-model="formulario[campo.key]"
              :type="campo.type || 'text'"
              :required="campo.required"
              :maxlength="campo.maxlength"
              :placeholder="campo.placeholder"
            />
          </div>
        </div>

        <div class="test-module-actions">
          <button type="submit" class="test-module-primary">Agregar registro</button>
        </div>
      </form>
    </section>

    <section class="test-module-section">
      <header class="test-module-section-heading">
        <h2>Registros capturados</h2>
        <span>{{ registros.length }} total</span>
      </header>

      <div v-if="!registros.length" class="test-module-empty">No hay registros para mostrar.</div>
      <div v-else class="test-module-records">
        <article v-for="(registro, index) in registros" :key="registro.id" class="test-module-record">
          <div class="test-module-record-header">
            <strong>{{ configuracion.registro }} {{ index + 1 }}</strong>
            <button type="button" class="test-module-remove" @click="eliminarRegistro(index)">Eliminar</button>
          </div>
          <dl>
            <template v-for="campo in configuracion.campos" :key="campo.key">
              <div v-if="valorRegistro(registro[campo.key])" class="test-module-record-field">
                <dt>{{ campo.label }}</dt>
                <dd>{{ valorRegistro(registro[campo.key]) }}</dd>
              </div>
            </template>
          </dl>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  tipo: { type: String, required: true },
});

const catalogo = {
  anexo_b: {
    titulo: "ANEXO B. INFORME DEL USO DE LA FUERZA",
    apartado: "Apartado B.1 Niveles del uso de la fuerza",
    instruccion: "Llene este anexo sólo en caso de lesionados y/o fallecidos con motivo del uso de la fuerza.",
    registro: "Registro",
    campos: [
      { key: "lesionados_autoridad", label: "Lesionados · Autoridad", type: "number", wide: true },
      { key: "lesionados_persona", label: "Lesionados · Persona", type: "number" },
      { key: "fallecidos_autoridad", label: "Fallecidos · Autoridad", type: "number" },
      { key: "fallecidos_persona", label: "Fallecidos · Persona", type: "number" },
      { key: "niveles", label: "Nivel del uso de la fuerza", type: "checks", wide: true, options: ["Reducción física de movimientos", "Armas incapacitantes menos letales", "Armas de fuego o fuerza letal"] },
      { key: "conductas", label: "Describa las conductas que motivaron el uso de la fuerza", type: "textarea", wide: true, required: true, rows: 4 },
      { key: "asistencia_medica", label: "¿Brindó o solicitó asistencia médica?", type: "select", options: ["Sí", "No"] },
      { key: "explicacion", label: "Explique", type: "textarea", wide: true },
      { key: "primer_respondiente", label: "Nombre del primer respondiente", wide: true },
    ],
  },
  anexo_d: {
    titulo: "ANEXO D. INVENTARIO DE ARMAS Y OBJETOS",
    apartado: "Apartado D.1 Registro de armas y objetos asegurados",
    instruccion: "Registre cada arma u objeto relacionado con el hecho en un renglón independiente.",
    registro: "Elemento",
    campos: [
      { key: "categoria", label: "Tipo de registro", type: "select", options: ["Arma", "Objeto"], required: true },
      { key: "tipo", label: "Tipo de arma u objeto", placeholder: "Ej. corta, larga, teléfono" },
      { key: "calibre", label: "Calibre" },
      { key: "color", label: "Color" },
      { key: "matricula", label: "Matrícula" },
      { key: "serie", label: "Número de serie" },
      { key: "ubicacion", label: "¿Dónde se encontró?", wide: true },
      { key: "observaciones", label: "Observaciones", type: "textarea", wide: true },
      { key: "destino", label: "Destino que se le dio", type: "textarea", wide: true },
      { key: "persona", label: "Persona a quien se aseguró", wide: true },
    ],
  },
  anexo_e: {
    titulo: "ANEXO E. ENTREVISTAS",
    apartado: "Apartado E.1 Datos de la entrevista",
    instruccion: "Capture una entrevista por registro. Evite incluir información real en este módulo de prueba.",
    registro: "Entrevista",
    campos: [
      { key: "fecha", label: "Fecha", type: "date", required: true },
      { key: "hora", label: "Hora", type: "time", required: true },
      { key: "entrevistado", label: "Nombre de la persona entrevistada", required: true, wide: true },
      { key: "calidad", label: "Calidad en la que participa", type: "select", options: ["Víctima", "Ofendido", "Testigo", "Denunciante", "Otra"] },
      { key: "lugar", label: "Lugar de la entrevista" },
      { key: "entrevistador", label: "Nombre del entrevistador", wide: true },
      { key: "relato", label: "Relato de la entrevista", type: "textarea", required: true, rows: 6 },
      { key: "observaciones", label: "Observaciones", type: "textarea" },
    ],
  },
  anexo_f: {
    titulo: "ANEXO F. ENTREGA - RECEPCIÓN DEL LUGAR DE LA INTERVENCIÓN",
    apartado: "Apartado F.1 Datos de la entrega - recepción",
    instruccion: "Registre la entrega y recepción del lugar de intervención.",
    registro: "Entrega",
    campos: [
      { key: "fecha", label: "Fecha", type: "date", required: true },
      { key: "hora", label: "Hora", type: "time", required: true },
      { key: "lugar", label: "Lugar de intervención", required: true, wide: true },
      { key: "entrega", label: "Nombre de quien entrega", required: true },
      { key: "adscripcion_entrega", label: "Adscripción de quien entrega" },
      { key: "recibe", label: "Nombre de quien recibe", required: true },
      { key: "adscripcion_recibe", label: "Adscripción de quien recibe" },
      { key: "estado_lugar", label: "Estado del lugar", type: "select", options: ["Preservado", "Procesado", "Sin preservación", "Otro"] },
      { key: "observaciones", label: "Observaciones", type: "textarea", wide: true },
    ],
  },
  bitacora: {
    titulo: "BITÁCORA",
    apartado: "Registro de actividad",
    instruccion: "Anote las actividades realizadas durante la captura del IPH.",
    registro: "Actividad",
    campos: [
      { key: "fecha", label: "Fecha", type: "date", required: true },
      { key: "hora", label: "Hora", type: "time", required: true },
      { key: "usuario", label: "Usuario", required: true },
      { key: "actividad", label: "Actividad", type: "select", options: ["Captura", "Modificación", "Revisión", "Entrega", "Otra"], required: true },
      { key: "descripcion", label: "Descripción", type: "textarea", required: true, wide: true },
    ],
  },
};

const configuracion = computed(() => catalogo[props.tipo] || catalogo.anexo_e);
const registros = ref([]);
const error = ref("");

function crearFormulario() {
  return Object.fromEntries(configuracion.value.campos.map((campo) => [
    campo.key,
    campo.type === "checks" ? [] : "",
  ]));
}

const formulario = ref(crearFormulario());

const storageKey = computed(() => `iph-pruebas:${props.iphId}:${props.tipo}`);

function valorRegistro(valor) {
  if (Array.isArray(valor)) return valor.join(", ");
  return valor == null ? "" : String(valor);
}

function cargarRegistros() {
  error.value = "";
  try {
    const guardados = localStorage.getItem(storageKey.value);
    registros.value = guardados ? JSON.parse(guardados) : [];
    if (!Array.isArray(registros.value)) throw new Error("Los datos guardados no tienen el formato esperado.");
  } catch (err) {
    console.error("No se pudieron cargar los registros de prueba:", err);
    error.value = "No se pudieron cargar los registros de prueba guardados en este navegador.";
    registros.value = [];
  }
}

function persistir(nuevosRegistros) {
  error.value = "";
  try {
    localStorage.setItem(storageKey.value, JSON.stringify(nuevosRegistros));
    registros.value = nuevosRegistros;
  } catch (err) {
    console.error("No se pudieron guardar los registros de prueba:", err);
    error.value = "No se pudieron guardar los cambios en este navegador.";
  }
}

function agregarRegistro() {
  persistir([...registros.value, { ...formulario.value, id: `${Date.now()}-${Math.random()}` }]);
  if (!error.value) formulario.value = crearFormulario();
}

function eliminarRegistro(indice) {
  persistir(registros.value.filter((_, i) => i !== indice));
}

watch(storageKey, cargarRegistros);
onMounted(cargarRegistros);
</script>
