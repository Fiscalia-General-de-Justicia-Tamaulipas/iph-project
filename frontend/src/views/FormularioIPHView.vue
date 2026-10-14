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
          :class="{ 'is-active': seccionActiva.id === seccion.id }"
          :aria-current="seccionActiva.id === seccion.id ? 'page' : undefined"
          :style="{ '--sidebar-order': index }"
          @click="navegarSeccion(seccion)"
        >
          <span class="iph-nav-icon" aria-hidden="true">{{ seccion.pendiente ? "◉" : "♟" }}</span>
          {{ seccion.etiqueta }}
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
            :disabled="exportando"
            @click="exportarPDF"
          >
            {{ exportando ? "GENERANDO..." : "EXPORTAR PDF" }}
          </button>
        </section>

        <section class="iph-section-card">
          <header class="iph-section-heading">
            <div>
              <p>Campo obligatorio*</p>
              <h1>{{ seccionActiva.titulo }}</h1>
            </div>
            <span v-if="seccionActiva.pendiente" class="iph-pending-badge">Pendiente de integrar</span>
          </header>

          <div v-if="seccionActiva.modulos.length" class="iph-section-content">
            <nav
              v-if="seccionActiva.id !== 'seccion-1'"
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
              @guardado="recargarEstado"
              @cancelar="irAlPanel"
              @siguiente="navegarSeccion(secciones[1])"
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
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
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
import NarracionPrimerRespondienteForm from "./modulos/NarracionPrimerRespondienteForm.vue";
import ActuacionesForm from "./modulos/ActuacionesForm.vue";
import AnexosPruebaForm from "./modulos/AnexosPruebaForm.vue";
import PuestaDisposicionForm from "./modulos/PuestaDisposicionForm.vue";

const props = defineProps({
  id: { type: [String, Number], required: true },
  modulo: { type: String, default: null },
});

const router = useRouter();
const auth = useAuthStore();
const iphId = computed(() => props.id);
const iph = ref(null);
const exportando = ref(false);
const anexosEntregados = ref({});

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
  narracion_primer_respondiente: NarracionPrimerRespondienteForm,
  actuaciones: ActuacionesForm,
  policias: PoliciasForm,
  anexo_b: AnexosPruebaForm,
  anexo_d: AnexosPruebaForm,
  anexo_e: AnexosPruebaForm,
  anexo_f: AnexosPruebaForm,
  bitacora: AnexosPruebaForm,
};

const secciones = [
  {
    id: "seccion-1",
    etiqueta: "SECCIÓN 1",
    titulo: "SECCIÓN 1. PUESTA A DISPOSICIÓN",
    pendiente: false,
    modulos: [{ clave: "puesta_disposicion", titulo: "Puesta a disposición" }],
  },
  {
    id: "seccion-2",
    etiqueta: "SECCIÓN 2",
    titulo: "SECCIÓN 2. PRIMER RESPONDIENTE",
    pendiente: false,
    modulos: [{ clave: "policias", titulo: "Datos del primer respondiente" }],
  },
  {
    id: "seccion-3",
    etiqueta: "SECCIÓN 3",
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
    titulo: "SECCIÓN 4. LUGAR DE LA INTERVENCIÓN",
    pendiente: false,
    modulos: [
      { clave: "inspeccion_lugar", titulo: "Inspección del lugar" },
    ],
  },
  {
    id: "seccion-5",
    etiqueta: "SECCIÓN 5",
    titulo: "SECCIÓN 5. NARRATIVA DE LOS HECHOS",
    pendiente: false,
    modulos: [{ clave: "narracion_primer_respondiente", titulo: "Narrativa y delitos" }],
  },
  {
    id: "anexo-a",
    etiqueta: "ANEXO A",
    titulo: "ANEXO A. DETENCIÓN(ES)",
    pendiente: false,
    modulos: [
      { clave: "imputado", titulo: "Datos de la persona detenida" },
      { clave: "inspeccion_persona", titulo: "Inspección a la persona detenida" },
    ],
  },
  {
    id: "anexo-b",
    etiqueta: "ANEXO B",
    titulo: "ANEXO B. INFORME DEL USO DE LA FUERZA",
    pendiente: false,
    modulos: [{ clave: "anexo_b", titulo: "Uso de la fuerza" }],
  },
  {
    id: "anexo-c",
    etiqueta: "ANEXO C",
    titulo: "ANEXO C. INSPECCIÓN DE VEHÍCULO",
    pendiente: false,
    modulos: [{ clave: "inspeccion_vehiculo", titulo: "Datos del vehículo inspeccionado" }],
  },
  {
    id: "anexo-d",
    etiqueta: "ANEXO D",
    titulo: "ANEXO D. INVENTARIO DE ARMAS Y OBJETOS",
    pendiente: false,
    modulos: [{ clave: "anexo_d", titulo: "Armas y objetos" }],
  },
  {
    id: "anexo-e",
    etiqueta: "ANEXO E",
    titulo: "ANEXO E. ENTREVISTAS",
    pendiente: false,
    modulos: [{ clave: "anexo_e", titulo: "Entrevistas" }],
  },
  {
    id: "anexo-f",
    etiqueta: "ANEXO F",
    titulo: "ANEXO F. ENTREGA - RECEPCIÓN DEL LUGAR DE LA INTERVENCIÓN",
    pendiente: false,
    modulos: [{ clave: "anexo_f", titulo: "Entrega - recepción" }],
  },
  {
    id: "bitacora",
    etiqueta: "BITÁCORA",
    titulo: "BITÁCORA DE ACTIVIDADES",
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

async function cargarIPH() {
  const { data } = await api.get(`/iph/${iphId.value}`);
  iph.value = data;
}

function recargarEstado() {
  cargarIPH();
}

async function exportarPDF() {
  exportando.value = true;
  try {
    const response = await api.get(`/iph/${iphId.value}/exportar-pdf`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `IPH_${folio.value}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } finally {
    exportando.value = false;
  }
}

watch(iphId, cargarIPH);
onMounted(cargarIPH);
</script>
