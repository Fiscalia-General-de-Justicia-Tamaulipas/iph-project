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
        :disabled="status === 'checking' || status === 'starting' || status === 'processing' || status === 'unsupported'"
        :aria-label="status === 'recording' ? 'Detener grabación' : 'Grabar dictado'"
        :aria-pressed="status === 'recording'"
        :title="status === 'recording' ? 'Detener y transcribir' : 'Grabar dictado en español'"
        @click="alternarDictado"
      >
        <svg v-if="status !== 'recording'" viewBox="0 0 24 24" aria-hidden="true">
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
import api from "../store/api";

// Deja margen para que el contenedor AAC/MP4 no exceda 60 s por padding del codificador.
const MAX_RECORDING_MS = 59_000;
const MAX_AUDIO_BYTES = 10 * 1024 * 1024;

const props = defineProps({
  target: { type: Object, default: null },
});

const status = ref("checking");
const mensaje = ref("");
const positionStyle = ref({ left: "0px", top: "0px" });
const mensajeVisible = computed(() => mensaje.value);

let mediaRecorder = null;
let mediaStream = null;
let audioChunks = [];
let recordingTimer = 0;
let positionFrame = 0;
let boundTarget = null;
let sessionId = 0;

function mostrarError(message) {
  status.value = "error";
  mensaje.value = `${message} Si lo prefieres, usa el micrófono del teclado del dispositivo.`;
}

function mensajePermiso(error) {
  if (error?.name === "NotAllowedError" || error?.name === "SecurityError") {
    const esIOS = /iPhone|iPad|iPod/.test(navigator.userAgent)
      || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
    return esIOS
      ? "Permiso de micrófono denegado. En iPad/iPhone revisa Ajustes > Safari > Micrófono y permite el acceso para este sitio."
      : "Permiso de micrófono denegado. Permite el acceso al micrófono en la configuración del navegador.";
  }
  if (error?.name === "NotFoundError" || error?.name === "DevicesNotFoundError") {
    return "No se encontró un micrófono disponible.";
  }
  if (error?.name === "NotReadableError" || error?.name === "TrackStartError") {
    return "El micrófono está ocupado o no se pudo iniciar. Cierra otras aplicaciones que lo estén usando e inténtalo de nuevo.";
  }
  if (!window.isSecureContext) return "El acceso al micrófono requiere HTTPS.";
  return "No se pudo iniciar la grabación. Revisa el permiso y la disponibilidad del micrófono.";
}

function mimePreferido() {
  if (typeof MediaRecorder === "undefined") return "";
  const ios = /iPhone|iPad|iPod/.test(navigator.userAgent)
    || (navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1);
  const candidatos = ios
    ? ["audio/mp4", "audio/mp4;codecs=mp4a.40.2", "audio/webm;codecs=opus", "audio/webm"]
    : ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/mp4;codecs=mp4a.40.2"];
  return candidatos.find((tipo) => MediaRecorder.isTypeSupported?.(tipo)) || "";
}

function liberarMicrofono() {
  if (recordingTimer) window.clearTimeout(recordingTimer);
  recordingTimer = 0;
  if (mediaStream) {
    mediaStream.getTracks().forEach((track) => track.stop());
    mediaStream = null;
  }
  mediaRecorder = null;
}

function insertarTexto(transcript, target) {
  if (!target || target !== boundTarget || !target.isConnected || target.disabled || target.readOnly) return;
  const texto = String(transcript || "").trim();
  if (!texto) throw new Error("El servicio no devolvió texto para insertar.");

  const valorActual = target.value;
  const inicio = Number.isInteger(target.selectionStart) ? target.selectionStart : valorActual.length;
  const fin = Number.isInteger(target.selectionEnd) ? target.selectionEnd : inicio;
  const antes = valorActual.slice(0, inicio);
  const despues = valorActual.slice(fin);
  const separadorInicial = antes && !/[\s¿¡([{]$/.test(antes) && !/^[,.;:!?…)}\]]/.test(texto) ? " " : "";
  const separadorFinal = despues && !/^\s/.test(despues) && !/^[,.;:!?…)}\]]/.test(despues) ? " " : "";
  target.setRangeText(`${separadorInicial}${texto}${separadorFinal}`, inicio, fin, "end");
  target.dispatchEvent(new Event("input", { bubbles: true }));
}

async function transcribir(blob, target, currentSession) {
  liberarMicrofono();
  if (!blob?.size) {
    if (currentSession === sessionId) mostrarError("La grabación quedó vacía. Inténtalo de nuevo.");
    return;
  }
  if (blob.size > MAX_AUDIO_BYTES) {
    if (currentSession === sessionId) mostrarError("La grabación supera el máximo de 10 MB.");
    return;
  }

  status.value = "processing";
  mensaje.value = "Procesando dictado de forma segura en el servidor institucional…";
  try {
    const body = new FormData();
    const extension = blob.type.includes("mp4") ? "mp4" : blob.type.includes("webm") ? "webm" : "audio";
    body.append("audio", blob, `dictado.${extension}`);
    const { data } = await api.post("/voz/transcribir", body, { timeout: 100_000 });
    if (currentSession !== sessionId || target !== boundTarget) return;
    insertarTexto(data?.text, target);
    status.value = "ready";
    mensaje.value = "Transcripción insertada. Puedes continuar escribiendo o grabar otra frase.";
  } catch (error) {
    if (currentSession !== sessionId) return;
    const code = error?.response?.data?.code;
    if (error?.response?.status === 429 || code === "voice_busy") {
      mostrarError("El servicio de voz está ocupado. Espera unos segundos y vuelve a intentarlo.");
    } else if (error?.code === "ECONNABORTED") {
      mostrarError("La transcripción tardó demasiado y se canceló. Tu campo se conservó; puedes volver a grabar.");
    } else if (error?.response?.status === 413) {
      mostrarError("El audio supera el límite permitido de 10 MB.");
    } else if (code === "audio_too_long") {
      mostrarError("La grabación superó los 60 segundos. Intenta una frase más corta.");
    } else if (code === "no_speech") {
      mostrarError("No se detectó voz en la grabación. Inténtalo de nuevo.");
    } else if (error?.response?.status === 401) {
      mostrarError("Tu sesión venció. Inicia sesión de nuevo y vuelve a intentar el dictado.");
    } else {
      mostrarError("No se pudo transcribir el audio en el servidor. El texto del campo se conservó.");
    }
  }
}

function detenerGrabacion(currentSession = sessionId) {
  const recorder = mediaRecorder;
  if (!recorder || recorder.state === "inactive") return;
  if (recordingTimer) window.clearTimeout(recordingTimer);
  recordingTimer = 0;
  mensaje.value = "Cerrando grabación…";
  recorder.onstop = () => {
    const blob = new Blob(audioChunks, { type: recorder.mimeType || audioChunks[0]?.type || "application/octet-stream" });
    audioChunks = [];
    void transcribir(blob, boundTarget, currentSession);
  };
  try {
    recorder.stop();
  } catch {
    liberarMicrofono();
    mostrarError("No se pudo cerrar la grabación correctamente.");
  }
}

async function iniciarGrabacion() {
  if (status.value === "recording" || status.value === "processing" || !props.target) return;
  const currentSession = ++sessionId;
  const target = props.target;
  audioChunks = [];

  if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") {
    mostrarError("Este navegador no permite grabar audio aquí. Verifica HTTPS y el soporte del micrófono.");
    return;
  }

  // getUserMedia se invoca de inmediato desde el handler del toque/clic.
  let streamPromise;
  try {
    streamPromise = navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true, channelCount: 1 } });
  } catch (error) {
    mostrarError(mensajePermiso(error));
    return;
  }

  status.value = "starting";
  mensaje.value = "Solicitando acceso al micrófono…";
  try {
    mediaStream = await streamPromise;
    if (currentSession !== sessionId || target !== boundTarget) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
      return;
    }
    const mimeType = mimePreferido();
    mediaRecorder = mimeType ? new MediaRecorder(mediaStream, { mimeType }) : new MediaRecorder(mediaStream);
    mediaRecorder.ondataavailable = (event) => {
      if (event.data?.size) audioChunks.push(event.data);
    };
    mediaRecorder.onerror = () => {
      mediaRecorder.onstop = null;
      liberarMicrofono();
      audioChunks = [];
      mostrarError("Ocurrió un problema al grabar. El contenido del campo no cambió.");
    };
    mediaRecorder.start(1000);
    status.value = "recording";
    mensaje.value = "Grabando. Toca el botón para detener y transcribir (máximo 60 segundos).";
    recordingTimer = window.setTimeout(() => detenerGrabacion(currentSession), MAX_RECORDING_MS);
    actualizarPosicion();
  } catch (error) {
    liberarMicrofono();
    audioChunks = [];
    if (currentSession === sessionId) mostrarError(mensajePermiso(error));
  }
}

function alternarDictado() {
  if (status.value === "recording") detenerGrabacion();
  else if (["ready", "stopped", "error"].includes(status.value)) void iniciarGrabacion();
}

function actualizarPosicion() {
  if (positionFrame) cancelAnimationFrame(positionFrame);
  positionFrame = requestAnimationFrame(() => {
    positionFrame = 0;
    const target = props.target;
    if (!target?.isConnected) return;
    const rect = target.getBoundingClientRect();
    const viewport = window.visualViewport;
    const viewportLeft = viewport?.offsetLeft || 0;
    const viewportTop = viewport?.offsetTop || 0;
    const viewportWidth = viewport?.width || window.innerWidth;
    const viewportHeight = viewport?.height || window.innerHeight;
    const rootStyle = getComputedStyle(document.documentElement);
    const safeTop = parseFloat(rootStyle.getPropertyValue("--safe-area-inset-top")) || 0;
    const safeRight = parseFloat(rootStyle.getPropertyValue("--safe-area-inset-right")) || 0;
    const safeBottom = parseFloat(rootStyle.getPropertyValue("--safe-area-inset-bottom")) || 0;
    const safeLeft = parseFloat(rootStyle.getPropertyValue("--safe-area-inset-left")) || 0;
    const buttonSize = 48;
    const x = Math.max(viewportLeft + safeLeft + 8, Math.min(rect.right - buttonSize - 6, viewportLeft + viewportWidth - buttonSize - safeRight - 8));
    const yDeseada = target instanceof HTMLTextAreaElement
      ? rect.bottom - buttonSize - 6
      : rect.top + (rect.height - buttonSize) / 2;
    const y = Math.max(viewportTop + safeTop + 8, Math.min(yDeseada, viewportTop + viewportHeight - buttonSize - safeBottom - 8));
    positionStyle.value = { left: `${x}px`, top: `${y}px` };
  });
}

watch(() => props.target, (target, previousTarget) => {
  sessionId += 1;
  if (mediaRecorder?.state === "recording") {
    mediaRecorder.onstop = null;
    try { mediaRecorder.stop(); } catch { /* La sesión pudo terminar entre el evento y stop(). */ }
  }
  liberarMicrofono();
  audioChunks = [];
  previousTarget?.classList?.remove("iph-dictation-target");
  boundTarget = target || null;

  if (!target) {
    status.value = "checking";
    mensaje.value = "";
    return;
  }
  target.classList?.add("iph-dictation-target");
  actualizarPosicion();
  const supported = typeof MediaRecorder !== "undefined" && !!navigator.mediaDevices?.getUserMedia;
  status.value = supported ? "ready" : "unsupported";
  mensaje.value = supported
    ? "Dictado privado: el audio se envía únicamente al servidor institucional para transcribirlo."
    : "Este navegador no permite grabar desde esta página. Puedes usar el micrófono del teclado.";
}, { immediate: true, flush: "sync" });

function escucharPosicion() { actualizarPosicion(); }

if (typeof window !== "undefined") {
  window.addEventListener("resize", escucharPosicion, { passive: true });
  window.addEventListener("scroll", escucharPosicion, { capture: true, passive: true });
  window.visualViewport?.addEventListener("resize", escucharPosicion, { passive: true });
  window.visualViewport?.addEventListener("scroll", escucharPosicion, { passive: true });
}

onBeforeUnmount(() => {
  sessionId += 1;
  if (mediaRecorder?.state === "recording") {
    mediaRecorder.onstop = null;
    try { mediaRecorder.stop(); } catch { /* Ya no hay grabación activa. */ }
  }
  liberarMicrofono();
  audioChunks = [];
  boundTarget?.classList?.remove("iph-dictation-target");
  window.removeEventListener("resize", escucharPosicion);
  window.removeEventListener("scroll", escucharPosicion, true);
  window.visualViewport?.removeEventListener("resize", escucharPosicion);
  window.visualViewport?.removeEventListener("scroll", escucharPosicion);
  if (positionFrame) cancelAnimationFrame(positionFrame);
});
</script>
