<template>
  <div class="iph-workspace">
    <header class="iph-topbar">
      <div class="iph-brand">
        <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" />
        <div class="iph-brand-links">
          <span class="iph-brand-title">Capturar Hecho Delictivo</span>
          <button type="button" @click="irAlPanel">Buscar</button>
          <button type="button" @click="irAlPanel">Inicio</button>
          <button type="button" @click="cerrarSesion">Salir</button>
        </div>
      </div>
      <div class="iph-user-summary">
        <span>USUARIO: {{ nombreUsuario }}</span>
        <span>NOMBRE: {{ nombreCompleto }}</span>
        <span>ENTIDAD: {{ adscripcion || "—" }}</span>
        <span>PUESTO: {{ puesto || "—" }}</span>
      </div>
    </header>

    <div class="iph-layout">
      <TransitionGroup name="sidebar-cascade" tag="nav" class="iph-sidebar" aria-label="Secciones del IPH">
        <button
          v-for="(seccion, index) in seccionesVisibles"
          :key="seccion.id"
          type="button"
          class="iph-nav-item"
          :class="{
            'is-active': seccionActiva.id === seccion.id,
            'is-section-two': seccion.id === 'seccion-2',
            'is-section-three': seccion.id === 'seccion-3',
          }"
          :aria-current="seccionActiva.id === seccion.id ? 'page' : undefined"
          :style="{ '--sidebar-order': index }"
          @click="navegarSeccion(seccion)"
        >
          <span class="iph-nav-icon" aria-hidden="true">{{ seccion.pendiente ? "◉" : "♟" }}</span>
          <span class="iph-nav-copy">
            <span class="iph-nav-label">{{ seccion.etiqueta }}</span>
            <small>{{ seccion.subtitulo }}</small>
          </span>
          <span
            v-if="seccionCompletada(seccion)"
            class="iph-nav-complete"
            :aria-label="`${seccion.etiqueta} completada`"
            title="Sección guardada"
          >✓</span>
        </button>
      </TransitionGroup>

      <main class="iph-main">
        <section class="iph-reference-card" aria-label="Datos de referencia del IPH">
          <div>
            <span class="iph-reference-label">Folio</span>
            <strong>{{ folio }}</strong>
          </div>
          <div>
            <span class="iph-reference-label">Número de referencia</span>
            <strong>{{ numeroReferencia }}</strong>
          </div>
          <div class="iph-reference-actions">
            <button
              type="button"
              class="iph-preview-button"
              :disabled="previsualizandoPantalla"
              @click="previsualizarPantalla"
            >
              {{ previsualizandoPantalla ? "GENERANDO VISTA PREVIA..." : "VISTA PREVIA PDF" }}
            </button>
            <button
              v-if="iph?.estado === 'ACTIVA'"
              type="button"
              class="iph-finish-button"
              :disabled="finalizando"
              @click="finalizarIPH"
            >
              {{ finalizando ? "FINALIZANDO..." : "FINALIZAR IPH" }}
            </button>
            <button
              v-if="seccionActiva.id === 'seccion-1'"
              type="button"
              class="iph-primary-button"
              disabled
              title="El flujo de supervisión aún no está integrado."
            >
              PARA SUPERVISAR
            </button>
            <button
              v-else
              type="button"
              class="iph-primary-button"
              :disabled="exportando || vistaPreviaCargando"
              @click="exportarPDF"
            >
              {{
                exportando
                  ? "GENERANDO..."
                  : iph?.estado === "TERMINADA"
                    ? "EXPORTAR PDF FINAL"
                    : "EXPORTAR VISTA PREVIA"
              }}
            </button>
            <p v-if="errorVistaPrevia" class="iph-preview-error" role="alert">
              {{ errorVistaPrevia }}
            </p>
          </div>
        </section>

        <section class="iph-section-card">
          <p v-if="errorEstado" class="test-module-error" role="alert">{{ errorEstado }}</p>
          <header class="iph-section-heading">
            <div>
              <p>Campo obligatorio*</p>
              <h1>{{ seccionActiva.titulo }}</h1>
            </div>
            <span v-if="seccionActiva.pendiente" class="iph-pending-badge">Pendiente de integrar</span>
          </header>

          <div
            v-if="seccionActiva.modulos.length"
            class="iph-section-content"
            @focusin="activarDictadoEnCampo"
            @focusout="limpiarDictadoEnCampo"
            @input="actualizarCamposVistaPrevia"
            @change="actualizarCamposVistaPrevia"
            @click="capturarDespuesDeAccion"
          >
            <nav
              v-if="seccionActiva.modulos.length > 1"
              class="iph-module-tabs"
              :aria-label="`Formularios de ${seccionActiva.etiqueta}`"
            >
              <button
                v-for="moduloItem in seccionActiva.modulos"
                :key="moduloItem.clave"
                type="button"
                :class="{ 'is-active': moduloActivo === moduloItem.clave }"
                @click="navegarModulo(moduloItem.clave)"
              >
                {{ moduloItem.titulo }}
              </button>
            </nav>

            <component
              :is="componenteActivo"
              v-if="componenteActivo"
              :key="moduloActivo"
              :iph-id="iphId"
              v-bind="propsFormulario"
              :tipo="moduloActivo"
              @guardado="marcarModuloCompletado"
              @cancelar="irAlPanel"
              @siguiente="marcarYAvanzar"
              @anexos-actualizados="actualizarAnexosVisibles"
            />
            <p v-else class="iph-empty-state">Selecciona un formulario para continuar.</p>
          </div>

          <div v-else class="iph-pending-content">
            <h2>{{ seccionActiva.titulo }}</h2>
            <p>
              Esta sección ya está contemplada en la navegación del IPH y queda preparada para integrar
              sus campos cuando se defina su contenido. No se han agregado campos ficticios ni se
              modificarán los datos existentes.
            </p>
          </div>
          <DictadoVoz :target="campoDictado" />
        </section>

        <section class="iph-preview-card" aria-labelledby="iph-preview-title">
          <header>
            <div>
              <p>Actualizada durante la captura</p>
              <h2 id="iph-preview-title">Vista previa del PDF</h2>
            </div>
            <span v-if="vistaPreviaCargando" role="status">Actualizando...</span>
          </header>
          <p v-if="errorVistaPrevia" class="test-module-error" role="alert">{{ errorVistaPrevia }}</p>
          <iframe
            v-if="pdfPreviewUrl"
            :key="pdfPreviewRevision"
            :src="pdfPreviewUrl"
            title="Vista previa del Informe Policial Homologado"
          />
          <p v-else class="iph-preview-empty">La vista previa aparecerá aquí al cargar el IPH.</p>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../store/api";
import { useAuthStore } from "../store/auth";

import ConocimientoHechoForm from "./modulos/ConocimientoHechoForm.vue";
import ActaNoticiaForm from "./modulos/ActaNoticiaForm.vue";
import AccionesRealizadasForm from "./modulos/AccionesRealizadasForm.vue";
import DenuncianteForm from "./modulos/DenuncianteForm.vue";
import PoliciasForm from "./modulos/PoliciasForm.vue";
import InspeccionLugarForm from "./modulos/InspeccionLugarForm.vue";
import InspeccionPersonaForm from "./modulos/InspeccionPersonaForm.vue";
import InspeccionVehiculoForm from "./modulos/InspeccionVehiculoForm.vue";
import AnexoAForm from "./modulos/AnexoAForm.vue";
import AnexoBForm from "./modulos/AnexoBForm.vue";
import AnexoCForm from "./modulos/AnexoCForm.vue";
import AnexoDForm from "./modulos/AnexoDForm.vue";
import AnexoEForm from "./modulos/AnexoEForm.vue";
import AnexoFForm from "./modulos/AnexoFForm.vue";
import BitacoraForm from "./modulos/BitacoraForm.vue";
import NarracionPrimerRespondienteForm from "./modulos/NarracionPrimerRespondienteForm.vue";
import ActuacionesForm from "./modulos/ActuacionesForm.vue";
import PuestaDisposicionForm from "./modulos/PuestaDisposicionForm.vue";
import DictadoVoz from "../components/DictadoVoz.vue";

const props = defineProps({
  id: { type: [String, Number], required: true },
  modulo: { type: String, default: null },
});

const router = useRouter();
const auth = useAuthStore();
const campoDictado = ref(null);

function activarDictadoEnCampo(event) {
  const elemento = event.target;
  if (!(elemento instanceof HTMLInputElement || elemento instanceof HTMLTextAreaElement)) {
    campoDictado.value = null;
    return;
  }

  const esCampoTexto = elemento instanceof HTMLTextAreaElement
    || elemento.type === "text"
    || elemento.type === "";
  campoDictado.value = esCampoTexto && !elemento.disabled && !elemento.readOnly
    ? elemento
    : null;
}

function limpiarDictadoEnCampo(event) {
  if (event.relatedTarget?.closest?.(".iph-dictation-control")) return;
  campoDictado.value = null;
}
const iphId = computed(() => props.id);
const iph = ref(null);
const exportando = ref(false);
const finalizando = ref(false);
const errorEstado = ref("");
const errorVistaPrevia = ref("");
const previsualizandoPantalla = ref(false);
const vistaPreviaCargando = ref(false);
const pdfPreviewUrl = ref("");
const pdfPreviewRevision = ref(0);
const camposPorModulo = ref({});
const anexosEntregados = ref({});
const modulosCompletados = ref(new Set());
let temporizadorVistaPrevia;
let solicitudVistaPrevia = 0;

const componentesPorModulo = {
  puesta_disposicion: PuestaDisposicionForm,
  conocimiento_hecho: ConocimientoHechoForm,
  acta_noticia: ActaNoticiaForm,
  acciones_realizadas: AccionesRealizadasForm,
  denunciante: DenuncianteForm,
  ofendido: DenuncianteForm,
  victima: DenuncianteForm,
  imputado: DenuncianteForm,
  testigo: DenuncianteForm,
  inspeccion_lugar: InspeccionLugarForm,
  inspeccion_persona: InspeccionPersonaForm,
  inspeccion_vehiculo: InspeccionVehiculoForm,
  inspeccion_vehiculos: InspeccionVehiculoForm,
  anexo_a: AnexoAForm,
  anexo_b: AnexoBForm,
  anexo_c: AnexoCForm,
  anexo_d: AnexoDForm,
  anexo_e: AnexoEForm,
  anexo_f: AnexoFForm,
  bitacora: BitacoraForm,
  narracion_primer_respondiente: NarracionPrimerRespondienteForm,
  actuaciones: ActuacionesForm,
  policias: PoliciasForm,
};

const secciones = [
  {
    id: "seccion-1",
    etiqueta: "SECCIÓN 1",
    subtitulo: "Puesta a disposición",
    titulo: "SECCIÓN 1. PUESTA A DISPOSICIÓN",
    pendiente: false,
    modulos: [{ clave: "puesta_disposicion", titulo: "Puesta a disposición" }],
  },
  {
    id: "seccion-2",
    etiqueta: "SECCIÓN 2",
    subtitulo: "Primer respondiente",
    titulo: "SECCIÓN 2. PRIMER RESPONDIENTE",
    pendiente: false,
    modulos: [{ clave: "policias", titulo: "Datos del primer respondiente" }],
  },
  {
    id: "seccion-3",
    etiqueta: "SECCIÓN 3",
    subtitulo: "Conocimiento del hecho",
    titulo: "SECCIÓN 3. CONOCIMIENTO DEL HECHO Y SEGUIMIENTO DE LA ACTUACIÓN DE LA AUTORIDAD",
    pendiente: false,
    modulos: [
      { clave: "conocimiento_hecho", titulo: "Conocimiento de hecho" },
      { clave: "acta_noticia", titulo: "Acta de noticia" },
      { clave: "acciones_realizadas", titulo: "Acciones realizadas" },
      { clave: "actuaciones", titulo: "Actuaciones" },
    ],
  },
  {
    id: "seccion-4",
    etiqueta: "SECCIÓN 4",
    subtitulo: "Lugar de la intervención",
    titulo: "SECCIÓN 4. LUGAR DE LA INTERVENCIÓN",
    pendiente: false,
    modulos: [
      { clave: "inspeccion_lugar", titulo: "Inspección del lugar" },
    ],
  },
  {
    id: "seccion-5",
    etiqueta: "SECCIÓN 5",
    subtitulo: "Narrativa de los hechos",
    titulo: "SECCIÓN 5. NARRATIVA DE LOS HECHOS",
    pendiente: false,
    modulos: [{ clave: "narracion_primer_respondiente", titulo: "Narrativa y delitos" }],
  },
  {
    id: "anexo-a",
    etiqueta: "ANEXO A",
    subtitulo: "Detención(es)",
    titulo: "ANEXO A. DETENCIÓN(ES)",
    pendiente: false,
    modulos: [{ clave: "anexo_a", titulo: "Detención(es)" }],
  },
  {
    id: "anexo-b",
    etiqueta: "ANEXO B",
    subtitulo: "Uso de la fuerza",
    titulo: "ANEXO B. INFORME DEL USO DE LA FUERZA",
    pendiente: false,
    modulos: [{ clave: "anexo_b", titulo: "Uso de la fuerza" }],
  },
  {
    id: "anexo-c",
    etiqueta: "ANEXO C",
    subtitulo: "Inspección de vehículo",
    titulo: "ANEXO C. INSPECCIÓN DE VEHÍCULO",
    pendiente: false,
    modulos: [{ clave: "anexo_c", titulo: "Inspección de vehículo" }],
  },
  {
    id: "anexo-d",
    etiqueta: "ANEXO D",
    subtitulo: "Inventario de armas y objetos",
    titulo: "ANEXO D. INVENTARIO DE ARMAS Y OBJETOS",
    pendiente: false,
    modulos: [{ clave: "anexo_d", titulo: "Armas y objetos" }],
  },
  {
    id: "anexo-e",
    etiqueta: "ANEXO E",
    subtitulo: "Entrevistas",
    titulo: "ANEXO E. ENTREVISTAS",
    pendiente: false,
    modulos: [{ clave: "anexo_e", titulo: "Entrevistas" }],
  },
  {
    id: "anexo-f",
    etiqueta: "ANEXO F",
    subtitulo: "Entrega y recepción del lugar",
    titulo: "ANEXO F. ENTREGA - RECEPCIÓN DEL LUGAR DE LA INTERVENCIÓN",
    pendiente: false,
    modulos: [{ clave: "anexo_f", titulo: "Entrega - recepción" }],
  },
  {
    id: "bitacora",
    etiqueta: "BITÁCORA",
    subtitulo: "Comentarios de registros devueltos",
    titulo: "BITÁCORA DE COMENTARIOS DE REGISTROS DEVUELTOS",
    pendiente: false,
    modulos: [{ clave: "bitacora", titulo: "Registro de actividad" }],
  },
];

const seccionesVisibles = computed(() => secciones.filter((seccion) => {
  const anexo = seccion.id.match(/^anexo-([a-f])$/i)?.[1]?.toUpperCase();
  return !anexo || anexosEntregados.value[anexo] === true;
}));

const modulosPersonasIndependientes = {
  denunciante: "Denunciante",
  ofendido: "Ofendido",
  victima: "Víctima",
  testigo: "Testigo",
};

const seccionActiva = computed(() => {
  const actual = secciones.find((seccion) => seccion.modulos.some((item) => item.clave === props.modulo));
  if (actual) return actual;
  if (modulosPersonasIndependientes[props.modulo]) {
    return {
      id: "personas-relacionadas",
      etiqueta: "PERSONAS",
      titulo: "PERSONAS RELACIONADAS",
      pendiente: false,
      modulos: [{ clave: props.modulo, titulo: modulosPersonasIndependientes[props.modulo] }],
    };
  }
  return secciones.find((seccion) => seccion.id === props.modulo) || secciones[0];
});

const moduloActivo = computed(() => {
  if (seccionActiva.value.modulos.some((item) => item.clave === props.modulo)) return props.modulo;
  return seccionActiva.value.modulos[0]?.clave || null;
});

const componenteActivo = computed(() => componentesPorModulo[moduloActivo.value] || null);
const propsFormulario = computed(() => moduloActivo.value === "puesta_disposicion"
  ? { iph: iph.value }
  : {});
const nombreUsuario = computed(() => auth.usuario?.usuario || "—");
const nombreCompleto = computed(() => auth.usuario?.nombre_completo || auth.usuario?.usuario || "—");
const adscripcion = computed(() => auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || "");
const puesto = computed(() => auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "");
const folio = computed(() => iph.value?.folio_interno || iph.value?.IPH || router.currentRoute.value.query.folio_interno || "Sin folio");
const numeroReferencia = computed(() => iph.value?.no_referencia || iph.value?.numero_referencia || iph.value?.NO_REFERENCIA || iph.value?.NUMERO_REFERENCIA || "—");

function navegarSeccion(seccion) {
  const destino = seccion.modulos[0]?.clave || seccion.id;
  router.push({ name: "formulario-iph", params: { id: iphId.value, modulo: destino } });
}

function avanzarSeccion() {
  const indiceActual = seccionesVisibles.value.findIndex((seccion) => seccion.id === seccionActiva.value.id);
  if (indiceActual < 0) return;
  const siguiente = seccionesVisibles.value[indiceActual + 1];
  if (siguiente) navegarSeccion(siguiente);
}

function seccionCompletada(seccion) {
  return seccion.modulos.length > 0 &&
    seccion.modulos.every((item) => modulosCompletados.value.has(item.clave));
}

function marcarModuloCompletado() {
  if (moduloActivo.value) {
    modulosCompletados.value = new Set(modulosCompletados.value).add(moduloActivo.value);
  }
  recargarEstado();
  programarVistaPrevia();
}

function marcarYAvanzar() {
  if (moduloActivo.value) {
    modulosCompletados.value = new Set(modulosCompletados.value).add(moduloActivo.value);
  }
  avanzarSeccion();
}

function navegarModulo(clave) {
  router.push({ name: "formulario-iph", params: { id: iphId.value, modulo: clave } });
}

function actualizarAnexosVisibles(entregados) {
  anexosEntregados.value = entregados;
  const anexoActual = seccionActiva.value.id.match(/^anexo-([a-f])$/i)?.[1]?.toUpperCase();
  if (anexoActual && entregados[anexoActual] !== true) {
    navegarSeccion(secciones[0]);
  }
}

function irAlPanel() {
  router.push({ name: "panel" });
}

function cerrarSesion() {
  auth.cerrarSesion();
  router.push({ name: "login" });
}

function leerCamposActuales() {
  const contenedor = document.querySelector(".iph-section-content");
  if (!contenedor || !moduloActivo.value) return;
  const controles = Array.from(contenedor.querySelectorAll("input, select, textarea"))
    .filter((control) => !["button", "submit", "reset", "hidden", "file"].includes(control.type));
  camposPorModulo.value = {
    ...camposPorModulo.value,
    [moduloActivo.value]: controles.map((control, index) => {
      const etiqueta = control.closest("label")?.textContent
        || (control.id
          ? Array.from(contenedor.querySelectorAll("label[for]")).find((label) => label.htmlFor === control.id)?.textContent
          : "")
        || control.getAttribute("aria-label")
        || control.name
        || `Campo ${index + 1}`;
      let value = control.value || "";
      if (control.type === "checkbox") value = control.checked ? (control.value === "on" ? "X" : control.value) : "";
      if (control.type === "radio") value = control.checked ? control.value : "";
      if (control.type === "date" && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
        const [year, month, day] = value.split("-");
        value = `${day}/${month}/${year}`;
      }
      return {
        label: etiqueta.replace(/\s+/g, " ").trim(),
        value: String(value).trim(),
      };
    }),
  };
}

function actualizarCamposVistaPrevia(event) {
  const control = event.target;
  if (!(control instanceof HTMLInputElement || control instanceof HTMLSelectElement || control instanceof HTMLTextAreaElement)) {
    return;
  }
  leerCamposActuales();
  programarVistaPrevia();
}

function programarVistaPrevia() {
  window.clearTimeout(temporizadorVistaPrevia);
  temporizadorVistaPrevia = window.setTimeout(actualizarVistaPrevia, 500);
}

async function previsualizarPantalla() {
  if (!moduloActivo.value) {
    errorVistaPrevia.value = "No se pudo identificar la pantalla actual para generar la vista previa.";
    return;
  }
  const ventana = window.open("", "_blank");
  if (!ventana) {
    errorVistaPrevia.value = "El navegador bloqueó la ventana de vista previa. Permite ventanas emergentes e inténtalo de nuevo.";
    return;
  }
  ventana.document.title = "Vista previa del IPH";
  ventana.document.body.textContent = "Generando la vista previa del PDF…";
  previsualizandoPantalla.value = true;
  errorVistaPrevia.value = "";
  try {
    leerCamposActuales();
    const { data } = await api.post(
      `/iph/${iphId.value}/capturas/${encodeURIComponent(moduloActivo.value)}/previsualizar-pdf`,
      { camposPorModulo: camposPorModulo.value },
      { responseType: "blob" },
    );
    const url = window.URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
    ventana.location.replace(url);
    window.setTimeout(() => window.URL.revokeObjectURL(url), 60000);
  } catch (error) {
    ventana.close();
    let mensaje = error.response?.data?.msg;
    if (error.response?.data instanceof Blob) {
      try {
        const payload = JSON.parse(await error.response.data.text());
        mensaje = payload.msg;
      } catch {
        mensaje = "";
      }
    }
    errorVistaPrevia.value = mensaje || "No se pudo generar la vista previa del PDF. Verifica que la captura esté guardada y vuelve a intentarlo.";
  } finally {
    previsualizandoPantalla.value = false;
  }
}

async function capturarDespuesDeAccion() {
  await nextTick();
  leerCamposActuales();
  programarVistaPrevia();
}

async function actualizarVistaPrevia() {
  const idSolicitud = ++solicitudVistaPrevia;
  vistaPreviaCargando.value = true;
  errorVistaPrevia.value = "";
  try {
    const { data } = await api.post(
      `/iph/${iphId.value}/previsualizar-pdf`,
      { camposPorModulo: camposPorModulo.value },
      { responseType: "blob" },
    );
    if (idSolicitud !== solicitudVistaPrevia) return;
    const urlAnterior = pdfPreviewUrl.value;
    pdfPreviewUrl.value = window.URL.createObjectURL(new Blob([data], { type: "application/pdf" }));
    pdfPreviewRevision.value += 1;
    if (urlAnterior) window.URL.revokeObjectURL(urlAnterior);
  } catch (error) {
    if (idSolicitud === solicitudVistaPrevia) {
      errorVistaPrevia.value = error.response?.data?.msg
        || "No se pudo actualizar la vista previa del PDF.";
    }
  } finally {
    if (idSolicitud === solicitudVistaPrevia) vistaPreviaCargando.value = false;
  }
}

async function cargarIPH() {
  const { data } = await api.get(`/iph/${iphId.value}`);
  iph.value = data;
  programarVistaPrevia();
}

function recargarEstado() {
  cargarIPH();
}

async function exportarPDF() {
  exportando.value = true;
  try {
    leerCamposActuales();
    const response = await api.post(
      `/iph/${iphId.value}/${iph.value?.estado === "TERMINADA" ? "exportar-pdf" : "previsualizar-pdf"}`,
      { camposPorModulo: camposPorModulo.value },
      { responseType: "blob" },
    );
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `IPH_${folio.value}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.setTimeout(() => window.URL.revokeObjectURL(url), 1000);
  } catch (error) {
    errorEstado.value = error.response?.data?.msg || "No se pudo exportar el PDF.";
  } finally {
    exportando.value = false;
  }
}

async function finalizarIPH() {
  if (!window.confirm("¿Confirma que desea marcar este IPH como terminado?")) return;
  finalizando.value = true;
  errorEstado.value = "";
  try {
    const { data } = await api.patch(`/iph/${iphId.value}/estado`, { estado: "TERMINADA" });
    iph.value = { ...iph.value, estado: data.estado };
  } catch (error) {
    errorEstado.value = error.response?.data?.msg || "No se pudo actualizar el estado del IPH.";
  } finally {
    finalizando.value = false;
  }
}

watch(iphId, (nuevoId, idAnterior) => {
  if (nuevoId !== idAnterior) {
    solicitudVistaPrevia += 1;
    window.clearTimeout(temporizadorVistaPrevia);
    modulosCompletados.value = new Set();
    camposPorModulo.value = {};
    if (pdfPreviewUrl.value) window.URL.revokeObjectURL(pdfPreviewUrl.value);
    pdfPreviewUrl.value = "";
  }
  cargarIPH();
});
onMounted(cargarIPH);
onBeforeUnmount(() => {
  solicitudVistaPrevia += 1;
  window.clearTimeout(temporizadorVistaPrevia);
  if (pdfPreviewUrl.value) window.URL.revokeObjectURL(pdfPreviewUrl.value);
});
</script>
