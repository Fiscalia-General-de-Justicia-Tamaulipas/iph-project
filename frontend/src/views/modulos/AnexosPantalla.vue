<template>
  <Teleport to="body">
    <Transition
      name="annex-screen"
      @after-enter="enfocarPantalla"
      @after-leave="restaurarPantalla"
    >
      <div
        v-if="abierta"
        ref="pantalla"
        class="annex-screen"
        :style="estilosPantalla"
        role="dialog"
        aria-modal="true"
        aria-labelledby="annex-screen-title"
        tabindex="-1"
        @keydown.capture="manejarTeclas"
      >
        <div class="annex-screen-blobs" aria-hidden="true">
          <span class="annex-screen-blob blob-one"></span>
          <span class="annex-screen-blob blob-two"></span>
          <span class="annex-screen-blob blob-three"></span>
        </div>

        <div
          v-if="ondaVisible"
          class="annex-screen-wave"
          :class="[`is-${colorOnda}`, { 'is-expanded': ondaExpandida }]"
          :style="estilosOnda"
          aria-hidden="true"
        ></div>

        <header class="annex-screen-header">
          <button
            type="button"
            class="annex-screen-icon-button annex-screen-back"
            aria-label="Regresar al anexo anterior"
            :disabled="procesando || (!esFinal && indiceActual === 0)"
            @click="regresar($event)"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7 7-7-7 7-7" /></svg>
          </button>

          <p class="annex-screen-brand">Registro de anexos IPH</p>

          <div
            class="annex-screen-progress"
            role="progressbar"
            :aria-valuenow="esFinal ? anexos.length : indiceActual + 1"
            aria-valuemin="0"
            :aria-valuemax="anexos.length"
            aria-label="Progreso del cuestionario"
          >
            <span class="annex-screen-progress-label">
              Pregunta {{ esFinal ? anexos.length : indiceActual + 1 }} de {{ anexos.length }}
            </span>
            <div class="annex-screen-segments" aria-hidden="true">
              <span
                v-for="(item, index) in anexos"
                :key="item.clave"
                :class="{
                  'is-done': respuestas[item.clave] !== null,
                  'is-active': index === indiceActual && !esFinal,
                }"
              >
                <i :style="{ width: respuestas[item.clave] !== null ? '100%' : index === indiceActual && !esFinal ? '38%' : '0%' }"></i>
              </span>
            </div>
          </div>

          <button
            type="button"
            class="annex-screen-icon-button annex-screen-close"
            aria-label="Cerrar pantalla de anexos"
            @click="solicitarCierre()"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18" /></svg>
          </button>
        </header>

        <div class="annex-screen-stage">
          <Transition
            :name="direccion === 'back' ? 'annex-content-back' : 'annex-content'"
            mode="out-in"
            @after-enter="alEntrarContenido"
          >
            <main
              v-if="!esFinal && !confirmacionVisible"
              :key="anexoActual.clave"
              class="annex-screen-content"
              aria-live="polite"
            >
              <Transition :name="direccion === 'back' ? 'annex-letter-back' : 'annex-letter'" mode="out-in">
                <span :key="anexoActual.clave" class="annex-screen-watermark" aria-hidden="true">{{ anexoActual.clave }}</span>
              </Transition>

              <p class="annex-screen-kicker">Anexo {{ indiceActual + 1 }} de {{ anexos.length }}</p>
              <h1 id="annex-screen-title">{{ anexoActual.nombre }}</h1>
              <p class="annex-screen-question">¿Se entrega este anexo?</p>

              <div class="annex-screen-choices">
                <button
                  :id="`annex-screen-${anexoActual.clave}-si`"
                  type="button"
                  class="annex-screen-choice is-yes"
                  :class="{ 'is-selected': respuestaAnimada === 'SI' }"
                  :disabled="procesando"
                  :style="estiloOndaBoton('SI')"
                  @click="responder('SI', $event)"
                >
                  <svg class="annex-choice-check" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12 4.5 4.5L19 7" /></svg>
                  <span>Sí</span>
                </button>
                <button
                  :id="`annex-screen-${anexoActual.clave}-no`"
                  type="button"
                  class="annex-screen-choice is-no"
                  :class="{ 'is-selected': respuestaAnimada === 'NO' }"
                  :disabled="procesando"
                  :style="estiloOndaBoton('NO')"
                  @click="responder('NO', $event)"
                >
                  <svg class="annex-choice-cross" viewBox="0 0 24 24" aria-hidden="true"><path d="m7 7 10 10M17 7 7 17" /></svg>
                  <span>No</span>
                </button>
              </div>

              <button type="button" class="annex-screen-none" :disabled="procesando" @click="ningunAnexo($event)">
                Ningún anexo
              </button>
            </main>

            <main
              v-else-if="confirmacionVisible"
              key="confirmation"
              class="annex-screen-content annex-screen-confirmation"
              role="status"
              tabindex="-1"
            >
              <span class="annex-confirmation-check" aria-hidden="true">
                <svg viewBox="0 0 48 48"><path d="m9 25 10 10L39 14" /></svg>
              </span>
              <h1 id="annex-screen-title">Respuesta registrada</h1>
              <p>Preparando siguiente pregunta...</p>
            </main>

            <main
              v-else
              :key="`final-${cantidadRespondidos}`"
              class="annex-screen-content annex-screen-finish"
              aria-live="polite"
            >
              <span class="annex-finish-mark" aria-hidden="true">
                <svg viewBox="0 0 48 48"><path d="m9 25 10 10L39 14" /></svg>
              </span>
              <p class="annex-screen-kicker">Revisión completa</p>
              <h1 id="annex-screen-title">{{ sinAnexos ? "No se entregan anexos" : "Anexos respondidos" }}</h1>
              <p class="annex-screen-finish-note">
                {{ sinAnexos ? "Todas las respuestas se registraron como No." : "Puedes tocar una respuesta para corregirla." }}
              </p>
              <TransitionGroup name="annex-final-chip" tag="div" class="annex-screen-summary">
                <button
                  v-for="(item, index) in respuestasListas"
                  :key="item.clave"
                  type="button"
                  class="annex-screen-chip"
                  :style="{ '--chip-delay': `${index * 55}ms` }"
                  :disabled="procesando"
                  @click="editarAnexo(item.clave)"
                >
                  {{ item.clave }} · {{ item.respuesta ? "Sí" : "No" }}
                </button>
              </TransitionGroup>
              <button type="button" class="annex-screen-continue" @click="solicitarCierre(true)">
                Continuar
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" /></svg>
              </button>
            </main>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";

const anexos = [
  { clave: "A", nombre: "Anexo A. Detención(es)" },
  { clave: "B", nombre: "Anexo B. Informe del uso de la fuerza" },
  { clave: "C", nombre: "Anexo C. Inspección de vehículo" },
  { clave: "D", nombre: "Anexo D. Inventario de armas y objetos" },
  { clave: "E", nombre: "Anexo E. Entrevistas" },
  { clave: "F", nombre: "Anexo F. Entrega-recepción del lugar de intervención" },
  { clave: "G", nombre: "Anexo G. Continuación de narrativa" },
];

const props = defineProps({
  abierta: { type: Boolean, default: false },
  respuestas: { type: Object, required: true },
  sinAnexos: { type: Boolean, default: false },
  cambiosPendientes: { type: Boolean, default: false },
  elementoDisparador: { type: Object, default: null },
  indiceInicial: { type: Number, default: 0 },
});

const emit = defineEmits(["cerrar", "actualizar-respuestas", "ningun-anexo", "editar-anexo"]);
const pantalla = ref(null);
const indiceActual = ref(0);
const direccion = ref("forward");
const procesando = ref(false);
const respuestaAnimada = ref("");
const confirmacionVisible = ref(false);
const ondaVisible = ref(false);
const ondaExpandida = ref(false);
const colorOnda = ref("yes");
const posicionOrigen = ref({ x: 0, y: 0 });
const posicionOnda = ref({ x: 0, y: 0 });
const enterResolver = ref(null);
const enterFallback = ref(null);
let secuencia = 0;
let bloqueoScroll = null;

const anexoActual = computed(() => anexos[indiceActual.value] || null);
const cantidadRespondidos = computed(() => anexos.filter(({ clave }) => props.respuestas[clave] !== null).length);
const respuestasListas = computed(() => anexos
  .filter(({ clave }) => props.respuestas[clave] !== null)
  .map(({ clave }) => ({ clave, respuesta: props.respuestas[clave] })));
const esFinal = computed(() => props.sinAnexos || indiceActual.value >= anexos.length);
const estilosPantalla = computed(() => ({
  "--origin-x": `${posicionOrigen.value.x}px`,
  "--origin-y": `${posicionOrigen.value.y}px`,
}));
const estilosOnda = computed(() => ({
  "--wave-x": `${posicionOnda.value.x}px`,
  "--wave-y": `${posicionOnda.value.y}px`,
}));

function primerPendiente() {
  const index = anexos.findIndex(({ clave }) => props.respuestas[clave] === null);
  return index < 0 ? anexos.length : index;
}

function ubicarOrigen(elemento = props.elementoDisparador) {
  const rect = elemento?.getBoundingClientRect();
  posicionOrigen.value = rect
    ? { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 }
    : { x: window.innerWidth / 2, y: window.innerHeight / 2 };
}

function bloquearScroll() {
  if (bloqueoScroll) return;
  bloqueoScroll = {
    x: window.scrollX,
    y: window.scrollY,
    body: {
      position: document.body.style.position,
      top: document.body.style.top,
      left: document.body.style.left,
      right: document.body.style.right,
      width: document.body.style.width,
      overflow: document.body.style.overflow,
    },
    htmlOverflow: document.documentElement.style.overflow,
  };
  document.documentElement.style.overflow = "hidden";
  Object.assign(document.body.style, {
    position: "fixed",
    top: `${-bloqueoScroll.y}px`,
    left: "0",
    right: "0",
    width: "100%",
    overflow: "hidden",
  });
}

function restaurarScroll() {
  if (!bloqueoScroll) return;
  const anterior = bloqueoScroll;
  bloqueoScroll = null;
  document.documentElement.style.overflow = anterior.htmlOverflow;
  Object.assign(document.body.style, anterior.body);
  window.scrollTo(anterior.x, anterior.y);
}

function resolverEntrada() {
  window.clearTimeout(enterFallback.value);
  enterFallback.value = null;
  const resolver = enterResolver.value;
  enterResolver.value = null;
  resolver?.();
}

function alEntrarContenido() {
  enfocarContenido();
  resolverEntrada();
}

async function enfocarContenido() {
  await nextTick();
  const destino = confirmacionVisible.value
    ? pantalla.value?.querySelector(".annex-screen-confirmation")
    : anexoActual.value
      ? document.getElementById(`annex-screen-${anexoActual.value.clave}-si`)
      : pantalla.value?.querySelector(".annex-screen-continue");
  destino?.focus({ preventScroll: true });
}

function enfocarPantalla() {
  enfocarContenido();
}

function restaurarPantalla() {
  restaurarScroll();
  props.elementoDisparador?.focus({ preventScroll: true });
}

function pausa(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function movimientoReducido() {
  return typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

async function expandirOnda(event, respuesta) {
  if (movimientoReducido()) return;
  const elemento = event?.currentTarget || event?.target;
  const rect = elemento?.getBoundingClientRect();
  const usaPuntero = Boolean(event?.detail && Number.isFinite(event.clientX) && Number.isFinite(event.clientY));
  posicionOnda.value = rect
    ? {
      x: usaPuntero ? event.clientX : rect.left + rect.width / 2,
      y: usaPuntero ? event.clientY : rect.top + rect.height / 2,
    }
    : { x: window.innerWidth / 2, y: window.innerHeight / 2 };
  colorOnda.value = respuesta === "SI" ? "yes" : "no";
  ondaVisible.value = true;
  ondaExpandida.value = false;
  await nextTick();
  requestAnimationFrame(() => {
    if (ondaVisible.value) ondaExpandida.value = true;
  });
}

function esperarEntrada() {
  return new Promise((resolve) => {
    enterResolver.value = resolve;
    enterFallback.value = window.setTimeout(resolverEntrada, 1100);
  });
}

async function transicionarA(indice, sentido, event, respuesta, antesDelCambio = null) {
  if (procesando.value) return;
  procesando.value = true;
  const accion = ++secuencia;
  respuestaAnimada.value = respuesta || "";
  if (!respuesta && event) await expandirOnda(event, "NO");

  if (respuesta) {
    await pausa(movimientoReducido() ? 120 : 220);
    if (accion !== secuencia) return;
    const entradaConfirmacion = esperarEntrada();
    confirmacionVisible.value = true;
    await nextTick();
    await entradaConfirmacion;
    if (accion !== secuencia) return;
    await pausa(movimientoReducido() ? 180 : 760);
  }
  if (accion !== secuencia) return;

  const claveAnterior = confirmacionVisible.value
    ? "confirmation"
    : esFinal.value ? "final" : anexoActual.value?.clave;
  antesDelCambio?.();
  direccion.value = sentido;
  indiceActual.value = indice;
  confirmacionVisible.value = false;
  const claveNueva = props.sinAnexos || indice >= anexos.length ? "final" : anexos[indice]?.clave;
  if (claveAnterior === claveNueva) {
    await nextTick();
    resolverEntrada();
  } else {
    const entrada = esperarEntrada();
    await nextTick();
    await entrada;
  }
  if (accion !== secuencia) return;

  if (ondaVisible.value) {
    ondaExpandida.value = false;
    await pausa(460);
    if (accion !== secuencia) return;
    ondaVisible.value = false;
  }
  respuestaAnimada.value = "";
  procesando.value = false;
}

function responder(respuesta, event) {
  if (procesando.value || !anexoActual.value) return;
  const actual = anexoActual.value;
  const respuestas = { ...props.respuestas, [actual.clave]: respuesta === "SI" };
  emit("actualizar-respuestas", respuestas);

  const siguiente = anexos.findIndex(({ clave }, index) => index > indiceActual.value && respuestas[clave] === null);
  const primeroPendiente = anexos.findIndex(({ clave }) => respuestas[clave] === null);
  const destino = siguiente >= 0 ? siguiente : primeroPendiente >= 0 ? primeroPendiente : anexos.length;
  transicionarA(destino, "forward", event, respuesta);
}

function regresar(event) {
  if (procesando.value) return;
  const destino = esFinal.value ? anexos.length - 1 : indiceActual.value - 1;
  if (destino < 0) return;
  transicionarA(destino, "back", event, "", props.sinAnexos ? () => emit("editar-anexo") : null);
}

function editarAnexo(clave) {
  if (procesando.value) return;
  const destino = anexos.findIndex((anexo) => anexo.clave === clave);
  if (destino < 0) return;
  if (props.sinAnexos) emit("editar-anexo", clave);
  direccion.value = destino < indiceActual.value ? "back" : "forward";
  indiceActual.value = destino;
}

function ningunAnexo(event) {
  if (procesando.value) return;
  emit("actualizar-respuestas", Object.fromEntries(anexos.map(({ clave }) => [clave, false])));
  transicionarA(anexos.length, "forward", event, "", () => emit("ningun-anexo"));
}

function estiloOndaBoton(respuesta) {
  return respuestaAnimada.value === respuesta
    ? { "--ripple-x": `${posicionOnda.value.x}px`, "--ripple-y": `${posicionOnda.value.y}px` }
    : undefined;
}

function solicitarCierre(continuar = false) {
  if (!continuar && props.cambiosPendientes && !window.confirm("Hay respuestas de anexos sin guardar. ¿Cerrar y conservarlas sin guardar?")) return;
  secuencia += 1;
  procesando.value = false;
  confirmacionVisible.value = false;
  ondaVisible.value = false;
  ondaExpandida.value = false;
  respuestaAnimada.value = "";
  resolverEntrada();
  emit("cerrar");
}

function elementosEnfocables() {
  return Array.from(pantalla.value?.querySelectorAll(
    'button:not(:disabled), [href], input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
  ) || []).filter((elemento) => elemento.getClientRects().length > 0);
}

function manejarTeclas(event) {
  if (event.key === "Escape") {
    event.preventDefault();
    solicitarCierre();
    return;
  }
  if (event.key === "Tab") {
    const elementos = elementosEnfocables();
    if (!elementos.length) {
      event.preventDefault();
      pantalla.value?.focus();
      return;
    }
    const primero = elementos[0];
    const ultimo = elementos[elementos.length - 1];
    if (event.shiftKey && (document.activeElement === primero || document.activeElement === pantalla.value)) {
      event.preventDefault();
      ultimo.focus();
    } else if (!event.shiftKey && document.activeElement === ultimo) {
      event.preventDefault();
      primero.focus();
    }
    return;
  }
  if (procesando.value) return;
  const tecla = event.key.toLowerCase();
  if (!esFinal.value && tecla === "s") {
    event.preventDefault();
    responder("SI", null);
  } else if (!esFinal.value && tecla === "n") {
    event.preventDefault();
    responder("NO", null);
  } else if (!esFinal.value && (event.key === "ArrowLeft" || event.key === "ArrowRight")) {
    event.preventDefault();
    document.getElementById(`annex-screen-${anexoActual.value.clave}-${event.key === "ArrowRight" ? "si" : "no"}`)?.focus();
  } else if (event.key === "Backspace") {
    event.preventDefault();
    regresar(null);
  }
}

watch(() => props.abierta, (abierta) => {
  if (abierta) {
    ubicarOrigen();
    indiceActual.value = props.indiceInicial >= anexos.length ? anexos.length : props.indiceInicial;
    if (indiceActual.value < 0 || !Number.isInteger(indiceActual.value)) indiceActual.value = primerPendiente();
    confirmacionVisible.value = false;
    bloquearScroll();
  }
}, { immediate: true });

onBeforeUnmount(() => {
  secuencia += 1;
  resolverEntrada();
  restaurarScroll();
});
</script>

<style scoped>
.annex-screen {
  --origin-x: 50vw;
  --origin-y: 50vh;
  position: fixed;
  z-index: 3000;
  inset: 0;
  display: flex;
  flex-direction: column;
  overflow: auto;
  overscroll-behavior: contain;
  padding: max(1rem, env(safe-area-inset-top)) max(1rem, env(safe-area-inset-right)) max(1rem, env(safe-area-inset-bottom)) max(1rem, env(safe-area-inset-left));
  background-image:
    linear-gradient(180deg, rgb(23 23 23 / 34%) 0%, rgb(23 23 23 / 46%) 55%, rgb(23 23 23 / 38%) 100%),
    url("/logos/iph-preguntas.jpg");
  background-position: center 48%;
  background-size: cover;
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: #fff;
  isolation: isolate;
}

.annex-screen-blobs {
  position: absolute;
  z-index: -1;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.annex-screen-blob {
  position: absolute;
  width: min(45vw, 36rem);
  aspect-ratio: 1;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.06;
  animation: annex-blob-float 25s ease-in-out infinite alternate;
}

.blob-one {
  top: -16%;
  left: -9%;
  background: #dadada;
}

.blob-two {
  right: -14%;
  bottom: -19%;
  background: #858585;
  animation-duration: 29s;
  animation-delay: -8s;
}

.blob-three {
  top: 43%;
  left: 47%;
  width: min(30vw, 25rem);
  background: #252525;
  animation-duration: 22s;
  animation-delay: -12s;
}

.annex-screen-wave {
  position: fixed;
  z-index: 4;
  inset: 0;
  background: var(--wave-color);
  clip-path: circle(0 at var(--wave-x) var(--wave-y));
  pointer-events: none;
  transition: clip-path 450ms cubic-bezier(.22, 1, .36, 1);
  will-change: clip-path;
}

.annex-screen-wave.is-yes {
  --wave-color: #dadada;
}

.annex-screen-wave.is-no {
  --wave-color: #252525;
}

.annex-screen-wave.is-expanded {
  clip-path: circle(150vmax at var(--wave-x) var(--wave-y));
}

.annex-screen-header {
  position: relative;
  z-index: 2;
  display: grid;
  width: min(920px, 100%);
  grid-template-columns: 2.85rem minmax(0, 1fr) 2.85rem;
  grid-template-areas:
    "back brand close"
    "progress progress progress";
  align-items: center;
  gap: clamp(0.7rem, 3vw, 2rem);
  margin: 0 auto;
  padding-top: 0.35rem;
}

.annex-screen-back {
  grid-area: back;
}

.annex-screen-brand {
  grid-area: brand;
  margin: 0;
  color: #dadada;
  font-size: clamp(0.88rem, 2vw, 1.08rem);
  font-weight: 750;
  letter-spacing: 0.12em;
  line-height: 1.2;
  text-align: center;
  text-transform: uppercase;
}

.annex-screen-close {
  grid-area: close;
}

.annex-screen-icon-button {
  display: grid;
  width: 2.85rem;
  height: 2.85rem;
  place-items: center;
  padding: 0;
  border: 1px solid rgb(218 218 218 / 42%);
  border-radius: 50%;
  background: rgb(23 23 23 / 40%);
  color: #fff;
  cursor: pointer;
  transition: background-color 180ms ease, transform 180ms ease;
}

.annex-screen-icon-button:hover:not(:disabled) {
  transform: scale(1.05);
  background: rgb(218 218 218 / 20%);
}

.annex-screen-icon-button:active:not(:disabled) {
  transform: scale(0.94);
}

.annex-screen-icon-button:disabled {
  opacity: 0.35;
  cursor: default;
}

.annex-screen-icon-button svg,
.annex-screen-continue svg {
  width: 1.25rem;
  height: 1.25rem;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.8;
}

.annex-screen-progress {
  display: grid;
  grid-area: progress;
  width: min(480px, 100%);
  justify-self: center;
  gap: 0.45rem;
}

.annex-screen-progress-label {
  color: rgb(218 218 218 / 88%);
  font-size: 0.76rem;
  font-weight: 650;
  letter-spacing: 0.11em;
  text-align: center;
  text-transform: uppercase;
}

.annex-screen-segments {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 0.32rem;
}

.annex-screen-segments > span {
  height: 0.3rem;
  overflow: hidden;
  border-radius: 999px;
  background: rgb(255 255 255 / 17%);
}

.annex-screen-segments i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #dadada;
  transition: width 600ms cubic-bezier(.22, 1, .36, 1);
}

.annex-screen-segments > span.is-done i {
  background: #fff;
}

.annex-screen-segments > span.is-active {
  animation: annex-segment-pulse 1.8s ease-in-out infinite;
}

.annex-screen-stage {
  display: flex;
  width: min(840px, 100%);
  min-height: 0;
  flex: 1;
  align-self: center;
  align-items: center;
  justify-content: center;
  perspective: 1300px;
  perspective-origin: center;
  transform-style: preserve-3d;
}

.annex-screen-content {
  position: relative;
  z-index: 1;
  box-sizing: border-box;
  display: flex;
  width: min(760px, 100%);
  min-height: clamp(22rem, 58svh, 35rem);
  flex: 0 1 auto;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: clamp(2rem, 8vh, 6rem) clamp(1.2rem, 5vw, 3rem);
  border: 1px solid rgb(218 218 218 / 38%);
  border-radius: clamp(1.25rem, 3vw, 2rem);
  background: rgb(23 23 23 / 40%);
  box-shadow: 0 1.2rem 3.5rem rgb(0 0 0 / 24%), inset 0 1px rgb(255 255 255 / 10%);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  text-align: center;
  isolation: isolate;
  transform-style: preserve-3d;
  backface-visibility: hidden;
}

.annex-screen-watermark {
  position: absolute;
  z-index: -1;
  top: 50%;
  left: 50%;
  color: rgb(218 218 218 / 8%);
  font-size: clamp(18rem, 62vh, 48rem);
  font-weight: 850;
  line-height: 0.8;
  pointer-events: none;
  transform: translate(-50%, -52%);
  user-select: none;
}

.annex-screen-kicker {
  margin: 0 0 clamp(0.7rem, 2vh, 1.25rem);
  color: #dadada;
  font-size: clamp(0.76rem, 1.5vw, 0.9rem);
  font-weight: 750;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.annex-screen-content h1 {
  max-width: 760px;
  margin: 0;
  color: #fff;
  font-size: clamp(2rem, 5.2vw, 4.35rem);
  font-weight: 650;
  letter-spacing: -0.045em;
  line-height: 1.08;
  text-wrap: balance;
}

.annex-screen-question {
  margin: clamp(1.1rem, 3vh, 2rem) 0 1.3rem;
  color: rgb(255 255 255 / 82%);
  font-size: clamp(0.95rem, 2vw, 1.2rem);
}

.annex-screen-choices {
  display: flex;
  justify-content: center;
  gap: clamp(0.8rem, 3vw, 1.5rem);
}

.annex-screen-choice {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  display: inline-flex;
  min-width: clamp(9.5rem, 22vw, 14rem);
  min-height: clamp(3.75rem, 8vh, 4.75rem);
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  padding: 0.9rem 1.6rem;
  border: 1px solid rgb(218 218 218 / 55%);
  border-radius: 999px;
  font-size: clamp(1.05rem, 2.5vw, 1.35rem);
  font-weight: 700;
  cursor: pointer;
  transition: transform 170ms ease, box-shadow 200ms ease, border-color 200ms ease;
}

.annex-screen-choice.is-yes {
  border-color: #fff;
  background: #dadada;
  color: #252525;
  box-shadow: 0 0.7rem 2rem rgb(0 0 0 / 16%);
}

.annex-screen-choice.is-no {
  background: #252525;
  color: #fff;
  box-shadow: 0 0.7rem 2rem rgb(0 0 0 / 14%);
}

.annex-screen-choice:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 1rem 2.4rem rgb(0 0 0 / 22%);
}

.annex-screen-choice:active:not(:disabled),
.annex-screen-choice.is-selected {
  transform: scale(0.95);
}

.annex-screen-choice.is-selected {
  border-color: #fff;
}

.annex-screen-choice:focus-visible,
.annex-screen-icon-button:focus-visible,
.annex-screen-none:focus-visible,
.annex-screen-chip:focus-visible,
.annex-screen-continue:focus-visible {
  outline: 3px solid #dadada;
  outline-offset: 4px;
}

.annex-screen-choice:disabled {
  cursor: wait;
}

.annex-choice-check,
.annex-choice-cross {
  position: relative;
  z-index: 1;
  width: 1.35rem;
  height: 1.35rem;
  fill: none;
  stroke: currentColor;
  stroke-dasharray: 26;
  stroke-dashoffset: 26;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.4;
}

.annex-screen-choice.is-selected .annex-choice-check {
  animation: annex-check-draw 180ms ease 35ms forwards;
}

.annex-screen-choice > span {
  position: relative;
  z-index: 1;
}

.annex-screen-none {
  margin-top: clamp(1.5rem, 4vh, 2.6rem);
  padding: 0.4rem 0.75rem;
  border: 0;
  border-bottom: 1px solid rgb(218 218 218 / 50%);
  background: transparent;
  color: rgb(218 218 218 / 88%);
  font-size: 0.86rem;
  cursor: pointer;
  transition: color 160ms ease, border-color 160ms ease;
}

.annex-screen-none:hover:not(:disabled) {
  border-color: #fff;
  color: #fff;
}

.annex-screen-none:disabled {
  opacity: 0.5;
}

.annex-screen-finish {
  max-width: 760px;
}

.annex-screen-confirmation {
  gap: 1rem;
}

.annex-confirmation-check {
  display: grid;
  width: clamp(4.5rem, 11vw, 6rem);
  height: clamp(4.5rem, 11vw, 6rem);
  flex: 0 0 auto;
  place-items: center;
  border: 1px solid #fff;
  border-radius: 50%;
  background: #dadada;
  box-shadow: 0 0 0 0.6rem rgb(218 218 218 / 12%), 0 0.8rem 2rem rgb(0 0 0 / 22%);
  color: #252525;
  animation: annex-finish-flash 500ms cubic-bezier(.22, 1, .36, 1) both;
}

.annex-confirmation-check svg {
  width: 58%;
  height: 58%;
  overflow: visible;
  fill: none;
  stroke: currentColor;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.7;
  animation: annex-check-draw 320ms ease 120ms forwards;
}

.annex-screen-confirmation h1 {
  font-size: clamp(1.8rem, 4.6vw, 3.2rem);
}

.annex-screen-confirmation p {
  margin: 0;
  color: rgb(255 255 255 / 82%);
  font-size: clamp(0.95rem, 1.8vw, 1.1rem);
}

.annex-finish-mark {
  position: relative;
  display: grid;
  width: clamp(4.5rem, 11vw, 7rem);
  height: clamp(4.5rem, 11vw, 7rem);
  place-items: center;
  margin-bottom: clamp(1.3rem, 4vh, 2.2rem);
  border: 1px solid rgb(218 218 218 / 55%);
  border-radius: 50%;
  background: rgb(218 218 218 / 16%);
  color: #dadada;
  animation: annex-finish-flash 700ms cubic-bezier(.22, 1, .36, 1) both;
}

.annex-finish-mark::before,
.annex-finish-mark::after {
  position: absolute;
  inset: -0.6rem;
  border: 1px solid rgb(218 218 218 / 32%);
  border-radius: 50%;
  content: "";
  animation: annex-finish-particles 900ms ease-out both;
}

.annex-finish-mark::after {
  inset: -1.15rem;
  opacity: 0.48;
  animation-delay: 80ms;
}

.annex-finish-mark svg {
  width: 58%;
  height: 58%;
  overflow: visible;
  fill: none;
  stroke: currentColor;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2.7;
  animation: annex-check-draw 380ms ease 150ms forwards;
}

.annex-screen-finish h1 {
  font-size: clamp(2rem, 4.6vw, 3.7rem);
}

.annex-screen-finish-note {
  margin: 0.9rem 0 0;
  color: rgb(255 255 255 / 76%);
  font-size: clamp(0.88rem, 1.7vw, 1rem);
}

.annex-screen-summary {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.55rem;
  margin-top: clamp(1.5rem, 4vh, 2.3rem);
}

.annex-screen-chip {
  min-height: 2.4rem;
  padding: 0.55rem 0.95rem;
  border: 1px solid rgb(218 218 218 / 38%);
  border-radius: 999px;
  background: rgb(23 23 23 / 48%);
  color: #fff;
  font-size: 0.82rem;
  font-weight: 650;
  cursor: pointer;
  transition: background-color 160ms ease, transform 160ms ease;
}

.annex-screen-chip:hover:not(:disabled) {
  transform: translateY(-2px);
  background: rgb(218 218 218 / 20%);
}

.annex-screen-continue {
  display: inline-flex;
  min-height: 3.25rem;
  align-items: center;
  justify-content: center;
  gap: 0.7rem;
  margin-top: clamp(1.6rem, 4vh, 2.5rem);
  padding: 0.8rem 1.5rem;
  border: 1px solid #fff;
  border-radius: 999px;
  background: #dadada;
  color: #252525;
  font-size: 0.95rem;
  font-weight: 750;
  cursor: pointer;
  transition: transform 170ms ease, background-color 170ms ease;
}

.annex-screen-continue:hover {
  transform: translateY(-2px);
  background: #fff;
}

.annex-screen-wave {
  transition: clip-path 450ms cubic-bezier(.22, 1, .36, 1);
}

.annex-screen-enter-active,
.annex-screen-leave-active {
  transition: clip-path 500ms cubic-bezier(.22, 1, .36, 1), opacity 380ms ease;
  will-change: clip-path, opacity;
}

.annex-screen-enter-from,
.annex-screen-leave-to {
  clip-path: circle(0 at var(--origin-x) var(--origin-y));
  opacity: 0.7;
}

.annex-content-enter-active,
.annex-content-back-enter-active {
  transition: transform 420ms cubic-bezier(.22, 1, .36, 1), opacity 420ms ease, filter 420ms ease;
  will-change: transform, opacity, filter;
}

.annex-content-leave-active,
.annex-content-back-leave-active {
  transition: transform 340ms cubic-bezier(.55, 0, .45, 1), opacity 340ms ease-in, filter 340ms ease-in;
  will-change: transform, opacity, filter;
}

.annex-content-enter-from {
  transform: rotateY(48deg) translateZ(-30px) scale(0.98);
  filter: blur(2px);
  opacity: 0;
}

.annex-content-leave-to {
  transform: rotateY(-48deg) translateZ(-30px) scale(0.97);
  filter: blur(2px);
  opacity: 0;
}

.annex-content-back-enter-from {
  transform: rotateY(-48deg) translateZ(-30px) scale(0.98);
  filter: blur(2px);
  opacity: 0;
}

.annex-content-back-leave-to {
  transform: rotateY(48deg) translateZ(-30px) scale(0.97);
  filter: blur(2px);
  opacity: 0;
}

.annex-content-enter-active .annex-screen-kicker,
.annex-content-back-enter-active .annex-screen-kicker {
  animation: annex-stagger 380ms cubic-bezier(.22, 1, .36, 1) 40ms both;
}

.annex-content-enter-active h1,
.annex-content-back-enter-active h1 {
  animation: annex-stagger 400ms cubic-bezier(.22, 1, .36, 1) 110ms both;
}

.annex-content-enter-active .annex-screen-choice:first-child,
.annex-content-back-enter-active .annex-screen-choice:first-child {
  animation: annex-stagger 400ms cubic-bezier(.22, 1, .36, 1) 180ms both;
}

.annex-content-enter-active .annex-screen-choice:nth-child(2),
.annex-content-back-enter-active .annex-screen-choice:nth-child(2) {
  animation: annex-stagger 400ms cubic-bezier(.22, 1, .36, 1) 250ms both;
}

.annex-content-enter-active .annex-finish-mark,
.annex-content-back-enter-active .annex-finish-mark {
  will-change: transform, opacity;
}

.annex-letter-enter-active,
.annex-letter-leave-active,
.annex-letter-back-enter-active,
.annex-letter-back-leave-active {
  transition: transform 360ms cubic-bezier(.22, 1, .36, 1), opacity 360ms ease;
  will-change: transform, opacity;
}

.annex-letter-enter-from,
.annex-letter-back-leave-to {
  transform: translate(-50%, calc(-50% + 50px));
  opacity: 0;
}

.annex-letter-leave-to,
.annex-letter-back-enter-from {
  transform: translate(-50%, calc(-50% - 50px));
  opacity: 0;
}

.annex-final-chip-enter-active,
.annex-final-chip-leave-active {
  transition: transform 260ms cubic-bezier(.22, 1, .36, 1), opacity 200ms ease;
  will-change: transform, opacity;
}

.annex-final-chip-enter-from,
.annex-final-chip-leave-to {
  transform: scale(0.8);
  opacity: 0;
}

.annex-final-chip-move {
  transition: transform 280ms cubic-bezier(.22, 1, .36, 1);
  will-change: transform;
}

.annex-final-chip-enter-active {
  animation: annex-stagger 350ms cubic-bezier(.22, 1, .36, 1) var(--chip-delay, 0ms) both;
}

@keyframes annex-stagger {
  from { transform: translateY(12px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes annex-check-draw {
  to { stroke-dashoffset: 0; }
}

@keyframes annex-finish-flash {
  0% { transform: scale(0.72); box-shadow: 0 0 0 0 rgb(218 218 218 / 35%); opacity: 0; }
  60% { transform: scale(1.06); box-shadow: 0 0 0 1rem rgb(218 218 218 / 0%); opacity: 1; }
  100% { transform: scale(1); box-shadow: 0 0 0 1rem rgb(218 218 218 / 0%); opacity: 1; }
}

@keyframes annex-finish-particles {
  from { transform: scale(0.55); opacity: 0.8; }
  to { transform: scale(1.24); opacity: 0; }
}

@keyframes annex-segment-pulse {
  50% { box-shadow: 0 0 0 4px rgb(218 218 218 / 15%); }
}

@keyframes annex-blob-float {
  from { transform: translate3d(-4%, 2%, 0) scale(0.94); }
  to { transform: translate3d(5%, -4%, 0) scale(1.08); }
}

@media (max-width: 640px) {
  .annex-screen {
    padding-right: max(0.85rem, env(safe-area-inset-right));
    padding-left: max(0.85rem, env(safe-area-inset-left));
  }

  .annex-screen-header {
    grid-template-columns: 2.7rem minmax(0, 1fr) 2.7rem;
    gap: 0.55rem;
  }

  .annex-screen-icon-button {
    width: 2.55rem;
    height: 2.55rem;
  }

  .annex-screen-content {
    min-height: min(32rem, calc(100svh - 7rem));
    padding: 2.4rem 1rem;
  }

  .annex-screen {
    background-position: 46% center;
  }

  .annex-screen-header {
    gap: 0.55rem;
  }

  .annex-screen-brand {
    font-size: clamp(0.78rem, 3vw, 0.98rem);
    letter-spacing: 0.08em;
  }

  .annex-screen-watermark {
    font-size: clamp(15rem, 60vh, 27rem);
  }

  .annex-screen-choices {
    width: min(100%, 26rem);
    gap: 0.6rem;
  }

  .annex-screen-choice {
    min-width: 0;
    min-height: 3.55rem;
    flex: 1;
    gap: 0.5rem;
    padding: 0.7rem 0.8rem;
  }

  .annex-screen-summary {
    gap: 0.4rem;
  }

  .annex-screen-chip {
    min-height: 2.2rem;
    padding: 0.45rem 0.7rem;
  }
}

@media (max-width: 380px) {
  .annex-screen-header {
    grid-template-columns: 2.4rem minmax(0, 1fr) 2.4rem;
    gap: 0.35rem;
  }

  .annex-screen-icon-button {
    width: 2.3rem;
    height: 2.3rem;
  }

  .annex-screen-choice {
    font-size: 1rem;
  }

  .annex-screen-brand {
    font-size: 0.72rem;
    letter-spacing: 0.04em;
  }
}

@media (prefers-reduced-motion: reduce) {
  .annex-screen-blob {
    animation: none;
  }

  .annex-screen-wave {
    display: none;
  }

  .annex-screen-enter-active,
  .annex-screen-leave-active,
  .annex-content-enter-active,
  .annex-content-back-enter-active,
  .annex-content-leave-active,
  .annex-content-back-leave-active,
  .annex-letter-enter-active,
  .annex-letter-leave-active,
  .annex-letter-back-enter-active,
  .annex-letter-back-leave-active,
  .annex-final-chip-enter-active,
  .annex-final-chip-leave-active {
    transition: opacity 180ms ease;
    filter: none;
  }

  .annex-screen-enter-from,
  .annex-screen-leave-to,
  .annex-content-enter-from,
  .annex-content-leave-to,
  .annex-content-back-enter-from,
  .annex-content-back-leave-to,
  .annex-letter-enter-from,
  .annex-letter-leave-to,
  .annex-letter-back-enter-from,
  .annex-letter-back-leave-to,
  .annex-final-chip-enter-from,
  .annex-final-chip-leave-to {
    clip-path: none;
    transform: none;
    filter: none;
  }

  .annex-content-enter-active .annex-screen-kicker,
  .annex-content-back-enter-active .annex-screen-kicker,
  .annex-content-enter-active h1,
  .annex-content-back-enter-active h1,
  .annex-content-enter-active .annex-screen-choice,
  .annex-content-back-enter-active .annex-screen-choice,
  .annex-final-chip-enter-active {
    animation: annex-reduced-fade 180ms ease both;
  }

  .annex-confirmation-check,
  .annex-confirmation-check svg {
    animation: none;
  }

  .annex-confirmation-check svg {
    stroke-dashoffset: 0;
  }

  .annex-finish-mark,
  .annex-finish-mark::before,
  .annex-finish-mark::after,
  .annex-finish-mark svg {
    animation: none;
  }

  .annex-finish-mark svg {
    stroke-dashoffset: 0;
  }

  .annex-screen-choice,
  .annex-screen-icon-button,
  .annex-screen-none,
  .annex-screen-chip,
  .annex-screen-continue {
    transition: none;
  }

  .annex-choice-check {
    animation: none;
    stroke-dashoffset: 0;
  }

  .annex-screen-segments > span.is-active {
    animation: none;
  }
}

@keyframes annex-reduced-fade {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
