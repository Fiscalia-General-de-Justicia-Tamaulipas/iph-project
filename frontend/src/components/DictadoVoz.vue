<template>
  <Teleport to="body">
    <div
      v-if="target"
      class="iph-dictation-control"
      :class="`is-${status}`"
      :style="positionStyle"
    >
      <button
        type="button"
        class="iph-dictation-button"
        :disabled="status === 'checking' || status === 'starting' || status === 'unsupported' || status === 'stopping'"
        :aria-label="status === 'listening' ? 'Detener dictado' : 'Iniciar dictado en español'"
        :aria-pressed="status === 'listening'"
        :title="status === 'listening' ? 'Detener dictado' : 'Dictado en español'"
        @click="alternarDictado"
      >
        <svg v-if="status !== 'listening'" viewBox="0 0 24 24" aria-hidden="true">
          <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 0 0-6 0v5a3 3 0 0 0 3 3Z" />
          <path d="M19 11a7 7 0 0 1-14 0M12 18v4m-4 0h8" />
        </svg>
        <svg v-else viewBox="0 0 24 24" aria-hidden="true">
          <rect x="6" y="6" width="12" height="12" rx="2" />
        </svg>
      </button>
      <span class="iph-dictation-status" role="status" aria-live="polite">{{ mensajeVisible }}</span>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";

const props = defineProps({
  target: { type: Object, default: null },
});

const status = ref("checking");
const mensaje = ref("");
const textoParcial = ref("");
const positionStyle = ref({ left: "0px", top: "0px" });
const mensajeVisible = computed(() => {
  if (status.value === "listening" && textoParcial.value) {
    return `Escuchando: ${textoParcial.value}`;
  }
  return mensaje.value;
});

let recognitionConstructor = null;
let recognition = null;
let requestId = 0;
let positionFrame = 0;
let processedResults = new Map();
let activeSessionStop = null;
let boundTarget = null;
let idiomaActual = 0;
const idiomas = ["es-MX", "es-US", "es-ES"];

function obtenerConstructor() {
  if (typeof window === "undefined") return null;
  return window.SpeechRecognition || window.webkitSpeechRecognition || null;
}

function setError(message) {
  status.value = "error";
  mensaje.value = message;
  textoParcial.value = "";
}

async function comprobarDisponibilidad(target, currentRequest) {
  recognitionConstructor = null;
  status.value = "checking";
  mensaje.value = "Verificando soporte de dictado…";
  textoParcial.value = "";

  const Constructor = obtenerConstructor();
  if (!Constructor) {
    status.value = "unsupported";
    mensaje.value = "Este navegador no admite SpeechRecognition. Puedes continuar escribiendo.";
    return;
  }
  if (currentRequest !== requestId || props.target !== target) return;
  recognitionConstructor = Constructor;
  status.value = "ready";
  mensaje.value = "Dictado disponible; se intentará es-MX y luego es-US/es-ES. El navegador puede procesar audio mediante su servicio de voz.";
}

function insertarTexto(transcript, currentRecognition) {
  const target = props.target;
  if (!target || target !== boundTarget || !target.isConnected || target.disabled || target.readOnly) return;
  if (recognition !== currentRecognition) return;

  const texto = String(transcript || "").trim();
  if (!texto) return;

  const valorActual = target.value;
  const inicio = Number.isInteger(target.selectionStart) ? target.selectionStart : valorActual.length;
  const fin = Number.isInteger(target.selectionEnd) ? target.selectionEnd : inicio;
  const antes = valorActual.slice(0, inicio);
  const despues = valorActual.slice(fin);
  const separadorInicial = antes
    && !/[\s¿¡([{]$/.test(antes)
    && !/^[,.;:!?…)}\]]/.test(texto)
    ? " "
    : "";
  const separadorFinal = despues
    && !/^\s/.test(despues)
    && !/^[,.;:!?…)}\]]/.test(despues)
    ? " "
    : "";
  const insercion = `${separadorInicial}${texto}${separadorFinal}`;

  try {
    target.setRangeText(insercion, inicio, fin, "end");
    target.dispatchEvent(new Event("input", { bubbles: true }));
  } catch {
    setError("No se pudo insertar el texto reconocido en este campo.");
  }
}

function quitarEventos(currentRecognition) {
  currentRecognition.onstart = null;
  currentRecognition.onresult = null;
  currentRecognition.onerror = null;
  currentRecognition.onend = null;
}

function abortarDictado(silent = false) {
  const currentRecognition = recognition;
  if (!currentRecognition) return;

  recognition = null;
  quitarEventos(currentRecognition);
  if (activeSessionStop === stopActiveSession) activeSessionStop = null;
  try {
    currentRecognition.abort();
  } catch {
    // La sesión puede haber terminado antes de recibir la orden de cierre.
  }

  status.value = silent ? "checking" : "stopped";
  mensaje.value = silent ? "" : "Dictado detenido.";
  textoParcial.value = "";
}

function stopActiveSession() {
  abortarDictado(true);
}

function detenerDictado() {
  const currentRecognition = recognition;
  if (!currentRecognition) return;
  status.value = "stopping";
  mensaje.value = "Deteniendo dictado…";
  textoParcial.value = "";
  try {
    currentRecognition.stop();
  } catch {
    abortarDictado(false);
  }
}

function explicarError(errorCode) {
  switch (errorCode) {
    case "not-allowed":
    case "service-not-allowed":
      return "Permiso de micrófono denegado. Autoriza el micrófono en el navegador y vuelve a intentar.";
    case "audio-capture":
      return "No se encontró un micrófono disponible.";
    case "network":
      return "Falló el servicio de reconocimiento o no hay conexión de red. Revisa la conexión o usa dictado on-premise.";
    case "language-not-supported":
    case "language-unavailable":
      return "El navegador no admite los idiomas es-MX, es-US ni es-ES.";
    case "no-speech":
      return "No se detectó voz. Puedes volver a intentarlo.";
    default:
      return "Ocurrió un error durante el dictado. Puedes continuar escribiendo manualmente.";
  }
}

function iniciarDictado() {
  if (!recognitionConstructor || !props.target || status.value === "checking") return;
  if (typeof window !== "undefined" && !window.isSecureContext) {
    setError("El micrófono requiere HTTPS. Para pruebas locales, usa localhost o el flag de Chrome --unsafely-treat-insecure-origin-as-secure=http://HOST:8080 (solo desarrollo). Puedes seguir escribiendo.");
    return;
  }

  if (activeSessionStop && activeSessionStop !== stopActiveSession) activeSessionStop();
  if (recognition) abortarDictado(true);

  try {
    const currentRecognition = new recognitionConstructor();
    idiomaActual = 0;
    currentRecognition.lang = idiomas[idiomaActual];
    currentRecognition.continuous = true;
    currentRecognition.interimResults = true;
    currentRecognition.maxAlternatives = 1;

    recognition = currentRecognition;
    boundTarget = props.target;
    processedResults = new Map();
    activeSessionStop = stopActiveSession;

    currentRecognition.onstart = () => {
      if (recognition !== currentRecognition) return;
      status.value = "listening";
      mensaje.value = "Escuchando en el dispositivo…";
    };

    currentRecognition.onresult = (event) => {
      if (recognition !== currentRecognition) return;
      let parcial = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const resultado = event.results[index];
        const transcript = resultado?.[0]?.transcript || "";
        if (resultado?.isFinal) {
          if (processedResults.get(index) === transcript) continue;
          processedResults.set(index, transcript);
          insertarTexto(transcript, currentRecognition);
        } else {
          parcial += transcript;
        }
      }
      textoParcial.value = parcial.trim();
    };

    currentRecognition.onerror = (event) => {
      if (recognition !== currentRecognition) return;
      if (["language-not-supported", "language-unavailable"].includes(event.error) && idiomaActual < idiomas.length - 1) {
        const siguienteIdioma = idiomas[idiomaActual + 1];
        const target = props.target;
        abortarDictado(true);
        idiomaActual += 1;
        mensaje.value = `es-MX no disponible; intentando ${siguienteIdioma}…`;
        status.value = "starting";
        iniciarConIdioma(target, siguienteIdioma);
        return;
      }
      setError(explicarError(event.error));
    };

    currentRecognition.onend = () => {
      if (recognition !== currentRecognition) return;
      recognition = null;
      if (activeSessionStop === stopActiveSession) activeSessionStop = null;
      if (status.value !== "error") {
        status.value = "stopped";
        mensaje.value = "Dictado detenido.";
        textoParcial.value = "";
      }
    };

    status.value = "starting";
    mensaje.value = `Iniciando reconocimiento (${idiomas[idiomaActual]})…`;
    currentRecognition.start();
  } catch {
    if (recognition) {
      const currentRecognition = recognition;
      recognition = null;
      quitarEventos(currentRecognition);
      try {
        currentRecognition.abort();
      } catch {
        // No hay sesión activa que pueda cerrarse.
      }
    }
    if (activeSessionStop === stopActiveSession) activeSessionStop = null;
    setError("No se pudo iniciar el reconocimiento. Revisa el permiso del micrófono, HTTPS y la conexión.");
  }
}

function alternarDictado() {
  if (status.value === "listening") {
    detenerDictado();
    return;
  }
  if (status.value === "ready" || status.value === "stopped" || status.value === "error") {
    iniciarDictado();
  }
}

function iniciarConIdioma(target, idioma) {
  try {
    const currentRecognition = new recognitionConstructor();
    currentRecognition.lang = idioma;
    currentRecognition.continuous = true;
    currentRecognition.interimResults = true;
    recognition = currentRecognition;
    boundTarget = target;
    activeSessionStop = stopActiveSession;
    currentRecognition.onstart = () => { if (recognition === currentRecognition) { status.value = "listening"; mensaje.value = `Escuchando (${idioma})…`; } };
    currentRecognition.onresult = (event) => {
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        if (event.results[index]?.isFinal) insertarTexto(event.results[index][0]?.transcript, currentRecognition);
        else textoParcial.value = event.results[index]?.[0]?.transcript || "";
      }
    };
    currentRecognition.onerror = (event) => {
      if (recognition !== currentRecognition) return;
      if (["language-not-supported", "language-unavailable"].includes(event.error) && idiomaActual < idiomas.length - 1) {
        const siguienteIdioma = idiomas[++idiomaActual];
        abortarDictado(true);
        status.value = "starting";
        mensaje.value = `Intentando ${siguienteIdioma}…`;
        iniciarConIdioma(target, siguienteIdioma);
      } else setError(explicarError(event.error));
    };
    currentRecognition.onend = () => { if (recognition === currentRecognition) { recognition = null; status.value = "stopped"; mensaje.value = "Dictado detenido."; } };
    currentRecognition.start();
  } catch {
    setError("No se pudo iniciar el micrófono. Revisa permiso, HTTPS y disponibilidad del dispositivo.");
  }
}

function actualizarPosicion() {
  if (positionFrame) cancelAnimationFrame(positionFrame);
  positionFrame = requestAnimationFrame(() => {
    positionFrame = 0;
    const target = props.target;
    if (!target?.isConnected) return;
    const rect = target.getBoundingClientRect();
    const x = Math.max(8, Math.min(rect.right - 46, window.innerWidth - 48));
    const y = Math.max(8, Math.min(rect.top + 6, window.innerHeight - 48));
    positionStyle.value = { left: `${x}px`, top: `${y}px` };
  });
}

watch(() => props.target, (target, previousTarget) => {
  requestId += 1;
  const currentRequest = requestId;
  abortarDictado(true);

  if (previousTarget?.classList) previousTarget.classList.remove("iph-dictation-target");
  boundTarget = target || null;
  recognitionConstructor = null;

  if (!target) {
    status.value = "checking";
    mensaje.value = "";
    return;
  }

  target.classList?.add("iph-dictation-target");
  actualizarPosicion();
  comprobarDisponibilidad(target, currentRequest);
}, { immediate: true, flush: "sync" });

function escucharPosicion() {
  actualizarPosicion();
}

if (typeof window !== "undefined") {
  window.addEventListener("resize", escucharPosicion, { passive: true });
  window.addEventListener("scroll", escucharPosicion, { capture: true, passive: true });
}

onBeforeUnmount(() => {
  requestId += 1;
  abortarDictado(true);
  boundTarget?.classList?.remove("iph-dictation-target");
  if (typeof window !== "undefined") {
    window.removeEventListener("resize", escucharPosicion);
    window.removeEventListener("scroll", escucharPosicion, true);
  }
  if (positionFrame) cancelAnimationFrame(positionFrame);
});
</script>
