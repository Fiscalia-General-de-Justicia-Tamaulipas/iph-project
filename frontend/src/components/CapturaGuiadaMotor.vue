<template>
  <section class="captura-guia" :aria-label="titulo">
    <header class="captura-guia-header">
      <div>
        <span>Captura guiada</span>
        <strong>{{ titulo }}</strong>
      </div>
      <div
        class="captura-guia-progreso"
        role="progressbar"
        :aria-valuenow="progresoActual"
        aria-valuemin="1"
        :aria-valuemax="preguntasActivas.length"
      >
        <span>Pregunta {{ progresoActual }} de {{ preguntasActivas.length }}</span>
        <div aria-hidden="true">
          <i :style="{ width: `${porcentajeProgreso}%` }"></i>
        </div>
      </div>
    </header>

    <div class="captura-guia-chat" ref="chat" aria-live="polite">
      <TransitionGroup name="captura-burbuja" tag="div" class="captura-guia-mensajes">
        <article
          v-for="mensaje in mensajes"
          :key="mensaje.id"
          class="captura-guia-conversacion"
        >
          <p class="captura-guia-burbuja sistema">{{ mensaje.pregunta }}</p>
          <p class="captura-guia-burbuja usuario">{{ mensaje.respuesta }}</p>
        </article>

        <article v-if="preguntaActual" :key="`actual-${preguntaActual.id}-${modoManual ? 'manual' : 'pregunta'}`" class="captura-guia-actual">
          <p class="captura-guia-burbuja sistema">{{ textoActual }}</p>
        </article>
      </TransitionGroup>

      <div v-if="preguntaActual?.tipo === 'resumen'" class="captura-guia-resumen">
        <dl>
          <template v-for="item in resumenItems" :key="item.etiqueta">
            <dt>{{ item.etiqueta }}</dt>
            <dd>{{ item.valor }}</dd>
          </template>
        </dl>
        <div class="captura-guia-aviso" role="alert">
          <span>Falta capturar los datos de quien recibe la puesta a disposición</span>
          <button type="button" @click="$emit('receptor')">
            Capturar receptor
          </button>
        </div>
        <p v-if="errorGuardado" class="captura-guia-error" role="alert">{{ errorGuardado }}</p>
        <div class="captura-guia-resumen-actions">
          <button type="button" class="captura-guia-secundario" @click="$emit('revisar-formulario')">
            Revisar en formulario completo
          </button>
          <button type="button" class="captura-guia-principal" :disabled="guardando" @click="$emit('guardar')">
            {{ guardando ? "Guardando..." : "Guardar sección" }}
          </button>
        </div>
      </div>

      <div v-else-if="preguntaActual" class="captura-guia-respuestas">
        <template v-if="preguntaActual.tipo === 'saludo'">
          <button type="button" class="captura-guia-principal" @click="responder('Comenzar')">
            Comenzar
          </button>
        </template>

        <template v-else-if="esSugerencia && !modoManual">
          <button type="button" class="captura-guia-principal" @click="aceptarSugerencia">
            Sí
          </button>
          <button type="button" class="captura-guia-secundario" @click="modoManual = true">
            No
          </button>
        </template>

        <template v-else-if="preguntaActual.tipo === 'si_no' && !modoManual">
          <button type="button" class="captura-guia-principal" @click="responderSiNo('SI')">
            Sí
          </button>
          <button type="button" class="captura-guia-secundario" @click="responderSiNo('NO')">
            No
          </button>
        </template>

        <template v-else>
          <label :for="`captura-${preguntaActual.id}`" class="captura-guia-campo">
            <span>{{ etiquetaCampo }}</span>
            <input
              :id="`captura-${preguntaActual.id}`"
              v-model="valorCaptura"
              :type="tipoEntrada"
              :required="Boolean(preguntaActual.obligatorio)"
              :maxlength="longitudMaxima"
              autocomplete="off"
            />
          </label>
          <p v-if="errorValidacion" class="captura-guia-error" role="alert">{{ errorValidacion }}</p>
          <button type="button" class="captura-guia-principal" @click="capturarTexto">
            Continuar
          </button>
        </template>
      </div>
    </div>

    <footer class="captura-guia-footer">
      <button
        type="button"
        class="captura-guia-atras"
        :disabled="indiceActual === 0 && !modoManual"
        @click="atras"
      >
        Atrás
      </button>
    </footer>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from "vue";

const props = defineProps({
  preguntas: { type: Array, required: true },
  datos: { type: Object, required: true },
  contexto: { type: Object, default: () => ({}) },
  titulo: { type: String, default: "Puesta a disposición" },
  resumenItems: { type: Array, default: () => [] },
  guardando: { type: Boolean, default: false },
  errorGuardado: { type: String, default: "" },
});

const emit = defineEmits(["actualizar", "guardar", "revisar-formulario", "receptor"]);

const indiceActual = ref(0);
const modoManual = ref(false);
const valorCaptura = ref("");
const errorValidacion = ref("");
const respuestas = ref({});
const mensajes = ref([]);
const chat = ref(null);

const preguntasActivas = computed(() => props.preguntas.filter((pregunta) =>
  pregunta.id === "resumen" ||
  !pregunta.mostrarSi ||
  pregunta.mostrarSi(props.datos, respuestas.value, props.contexto),
));

const preguntaActual = computed(() => preguntasActivas.value[indiceActual.value] || null);
const progresoActual = computed(() => Math.min(indiceActual.value + 1, preguntasActivas.value.length));
const porcentajeProgreso = computed(() => {
  const total = preguntasActivas.value.length || 1;
  return Math.round((progresoActual.value / total) * 100);
});

const textoActual = computed(() => {
  if (!preguntaActual.value) return "";
  if (typeof preguntaActual.value.pregunta === "function") {
    return preguntaActual.value.pregunta(props.datos, respuestas.value, props.contexto);
  }
  return preguntaActual.value.pregunta;
});

const esSugerencia = computed(() => {
  if (!preguntaActual.value) return false;
  return typeof preguntaActual.value.sugerencia === "function";
});

const tipoEntrada = computed(() => {
  if (preguntaActual.value?.tipo === "fecha") return "date";
  if (preguntaActual.value?.tipo === "hora") return "time";
  return "text";
});
const longitudMaxima = computed(() => preguntaActual.value?.tipo === "texto" ? 150 : undefined);
const etiquetaCampo = computed(() => {
  const etiquetas = {
    fecha: "Fecha",
    hora: "Hora",
    texto: "Respuesta",
  };
  return etiquetas[preguntaActual.value?.tipo] || "Respuesta";
});

function obtenerValor(ruta) {
  return ruta.split(".").reduce((actual, parte) => actual?.[parte], props.datos);
}

function establecerValor(ruta, valor) {
  emit("actualizar", { ruta, valor });
}

function desplazarAlFinal() {
  nextTick(() => {
    if (chat.value) chat.value.scrollTop = chat.value.scrollHeight;
  });
}

function avanzar() {
  modoManual.value = false;
  errorValidacion.value = "";
  valorCaptura.value = "";
  indiceActual.value = Math.min(indiceActual.value + 1, preguntasActivas.value.length - 1);
  desplazarAlFinal();
}

function registrarMensaje(respuesta) {
  mensajes.value.push({
    id: `${preguntaActual.value.id}-${mensajes.value.length}`,
    pregunta: textoActual.value,
    respuesta,
  });
  desplazarAlFinal();
}

function responder(respuesta) {
  respuestas.value[preguntaActual.value.id] = "SI";
  registrarMensaje(respuesta);
  avanzar();
}

function aceptarSugerencia() {
  const pregunta = preguntaActual.value;
  const valor = pregunta.sugerencia(props.datos, respuestas.value, props.contexto);
  establecerValor(pregunta.campoFormulario, valor);
  respuestas.value[pregunta.id] = "SI";
  registrarMensaje("Sí");
  avanzar();
}

function responderSiNo(valor) {
  const pregunta = preguntaActual.value;
  respuestas.value[pregunta.id] = valor;

  if (pregunta.id === "numero_expediente") {
    if (valor === "NO") establecerValor("no_expediente", "");
  } else if (pregunta.id === "responsable_sesion") {
    if (valor === "SI") {
      establecerValor("responsable.primer_apellido", props.contexto.primerApellido || "");
      establecerValor("responsable.segundo_apellido", props.contexto.segundoApellido || "");
      establecerValor("responsable.nombres", props.contexto.nombres || "");
      establecerValor("responsable.adscripcion", props.contexto.adscripcion || "");
      establecerValor("responsable.cargo", props.contexto.cargo || "");
    }
  } else if (pregunta.campoFormulario) {
    establecerValor(pregunta.campoFormulario, valor);
  }

  registrarMensaje(valor === "SI" ? "Sí" : "No");
  avanzar();
}

function capturarTexto() {
  const pregunta = preguntaActual.value;
  const valor = valorCaptura.value.trim();
  if (pregunta.obligatorio && !valor) {
    errorValidacion.value = "Este dato es obligatorio.";
    return;
  }
  if (pregunta.campoFormulario) establecerValor(pregunta.campoFormulario, valor);
  respuestas.value[pregunta.id] = valor;
  registrarMensaje(valor || "Sin dato");
  avanzar();
}

function atras() {
  errorValidacion.value = "";
  if (modoManual.value) {
    modoManual.value = false;
    valorCaptura.value = "";
    return;
  }
  if (indiceActual.value <= 0) return;

  const anteriorId = preguntasActivas.value[indiceActual.value - 1]?.id;
  if (anteriorId) delete respuestas.value[anteriorId];
  modoManual.value = false;
  nextTick(() => {
    const nuevoIndice = preguntasActivas.value.findIndex((pregunta) => pregunta.id === anteriorId);
    indiceActual.value = nuevoIndice >= 0 ? nuevoIndice : Math.max(0, indiceActual.value - 1);
  });
  const anterior = anteriorId
    ? preguntasActivas.value.find((pregunta) => pregunta.id === anteriorId)
    : null;
  valorCaptura.value = anterior?.campoFormulario ? obtenerValor(anterior.campoFormulario) || "" : "";
  desplazarAlFinal();
}

watch(preguntaActual, (actual) => {
  modoManual.value = false;
  valorCaptura.value = actual?.campoFormulario ? obtenerValor(actual.campoFormulario) || "" : "";
  errorValidacion.value = "";
  desplazarAlFinal();
});

watch(() => props.datos, desplazarAlFinal, { deep: true });
</script>

<style scoped>
.captura-guia {
  --guinda-chat: #6b1d3f;
  display: grid;
  min-height: 520px;
  grid-template-rows: auto minmax(330px, 1fr) auto;
  overflow: hidden;
  border: 1px solid #d8d8d8;
  border-radius: 12px;
  background: #f7f7f7;
  color: #292929;
}

.captura-guia-header {
  display: flex;
  min-height: 72px;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-bottom: 1px solid #dedede;
  background: #fff;
}

.captura-guia-header > div:first-child {
  display: grid;
  gap: 0.15rem;
}

.captura-guia-header span {
  color: #777;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
}

.captura-guia-header strong {
  font-size: 0.9rem;
}

.captura-guia-progreso {
  width: min(250px, 42%);
}

.captura-guia-progreso > span {
  display: block;
  margin-bottom: 0.35rem;
  text-align: right;
}

.captura-guia-progreso > div {
  height: 5px;
  overflow: hidden;
  border-radius: 999px;
  background: #dedede;
}

.captura-guia-progreso i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--guinda-chat);
  transition: width 280ms ease;
}

.captura-guia-chat {
  max-height: 470px;
  overflow-y: auto;
  padding: 1rem;
}

.captura-guia-mensajes {
  display: grid;
  gap: 0.65rem;
}

.captura-guia-conversacion,
.captura-guia-actual {
  display: grid;
  gap: 0.35rem;
}

.captura-guia-burbuja {
  width: fit-content;
  max-width: min(78%, 660px);
  margin: 0;
  padding: 0.72rem 0.85rem;
  border-radius: 16px;
  font-size: 0.82rem;
  line-height: 1.42;
}

.captura-guia-burbuja.sistema {
  justify-self: start;
  border-bottom-left-radius: 4px;
  background: #e8e8e8;
  color: #3d3d3d;
}

.captura-guia-burbuja.usuario {
  justify-self: end;
  border-bottom-right-radius: 4px;
  background: #343434;
  color: #fff;
}

.captura-guia-respuestas {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.55rem;
  margin-top: 0.8rem;
}

.captura-guia-respuestas button,
.captura-guia-resumen-actions button,
.captura-guia-atras {
  min-height: 44px;
  padding: 0.65rem 1rem;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 800;
}

.captura-guia-principal {
  border: 1px solid var(--guinda-chat);
  background: var(--guinda-chat);
  color: #fff;
}

.captura-guia-secundario,
.captura-guia-atras {
  border: 1px solid #cfcfcf;
  background: #fff;
  color: #555;
}

.captura-guia-campo {
  display: grid;
  width: 100%;
  gap: 0.35rem;
  color: #555;
  font-size: 0.72rem;
  font-weight: 700;
}

.captura-guia-campo input {
  width: 100%;
  min-height: 44px;
  padding: 0.6rem 0.75rem;
  border: 1px solid #bbb;
  border-radius: 8px;
  background: #fff;
  color: #292929;
  font-size: 0.85rem;
}

.captura-guia-error {
  width: 100%;
  margin: 0;
  color: #9c2f2f;
  font-size: 0.72rem;
}

.captura-guia-resumen {
  margin-top: 0.8rem;
  border: 1px solid #dedede;
  border-radius: 10px;
  background: #fff;
  padding: 0.8rem;
}

.captura-guia-resumen dl {
  display: grid;
  grid-template-columns: minmax(150px, 0.35fr) 1fr;
  gap: 0.45rem 0.8rem;
  margin: 0;
}

.captura-guia-resumen dt {
  color: #777;
  font-size: 0.72rem;
  font-weight: 700;
}

.captura-guia-resumen dd {
  margin: 0;
  font-size: 0.78rem;
}

.captura-guia-aviso {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin: 0.8rem 0 0;
  padding: 0.65rem 0.75rem;
  border-left: 4px solid var(--guinda-chat);
  background: #f5edf1;
  color: #5c293f;
  font-size: 0.75rem;
  font-weight: 700;
}

.captura-guia-aviso button {
  min-height: 44px;
  flex: 0 0 auto;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--guinda-chat);
  border-radius: 8px;
  background: #fff;
  color: var(--guinda-chat);
  font-size: 0.72rem;
  font-weight: 800;
}

.captura-guia-resumen-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.55rem;
  margin-top: 0.8rem;
}

.captura-guia-footer {
  display: flex;
  min-height: 58px;
  align-items: center;
  padding: 0.65rem 1rem;
  border-top: 1px solid #dedede;
  background: #fff;
}

.captura-guia-atras:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.captura-burbuja-enter-active,
.captura-burbuja-move {
  transition: opacity 220ms ease, transform 260ms ease;
}

.captura-burbuja-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 640px) {
  .captura-guia {
    min-height: 480px;
  }

  .captura-guia-header {
    align-items: flex-start;
  }

  .captura-guia-progreso {
    width: 48%;
  }

  .captura-guia-burbuja {
    max-width: 88%;
  }

  .captura-guia-respuestas button,
  .captura-guia-resumen-actions button {
    flex: 1 1 150px;
  }

  .captura-guia-resumen dl {
    grid-template-columns: 1fr;
  }

  .captura-guia-resumen dd {
    margin-bottom: 0.25rem;
  }
}

@media (prefers-reduced-motion: reduce) {
  .captura-burbuja-enter-active,
  .captura-burbuja-move,
  .captura-guia-progreso i {
    transition: none;
  }
}
</style>
