<template>
  <div class="min-h-screen bg-[#efefef]">
    <header class="bg-[#575756] text-white px-6 py-4 shadow-sm">
      <div class="max-w-7xl mx-auto flex justify-between items-center gap-4">
        <div>
          <button @click="$router.push({ name: 'panel' })" class="text-xs text-[#dadada] hover:text-white hover:underline">← Volver al panel</button>
          <h1 class="font-bold text-lg mt-2">IPH — Folio {{ iph?.folio_interno }}</h1>
        </div>
        <div class="flex items-center gap-2">
          <button
            v-if="moduloActivo"
            @click="volverAlArbol"
            class="bg-[#dadada] text-[#575756] px-3 py-2 rounded-md text-sm font-semibold hover:bg-[#cfcfcf]"
          >
            Volver al árbol
          </button>
          <button
            @click="exportarPDF"
            :disabled="exportando"
            class="bg-[#878787] text-white px-4 py-2 rounded-md hover:bg-[#6d6d6d] disabled:opacity-50"
          >
            {{ exportando ? "Generando..." : "Exportar a PDF" }}
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6">
      <div v-if="!moduloActivo" class="mx-auto max-w-4xl">
        <div class="rounded-[32px] border border-[#d7d7d7] bg-white shadow-[0_20px_50px_rgba(87,87,86,0.08)] overflow-hidden">
          <div class="bg-[#575756] px-6 py-4 text-center text-white">
            <p class="text-[10px] uppercase tracking-[0.28em] text-[#dadada]">Expediente</p>
            <h2 class="mt-2 text-2xl font-black">Árbol del IPH</h2>
          </div>

          <div class="p-6">
            <div class="mb-6 rounded-2xl border border-[#ececec] bg-[#f7f7f7] px-4 py-3">
              <div class="flex items-center justify-between gap-3">
                <div>
                  <p class="text-[10px] uppercase tracking-[0.24em] text-[#878787]">Progreso</p>
                  <p class="mt-1 text-sm font-bold text-[#575756]">Avance del expediente</p>
                </div>
                <span class="rounded-full border border-[#d9d9d9] bg-white px-3 py-1 text-sm font-bold text-[#575756]">{{ modulosCompletados }}/{{ modulos.length }}</span>
              </div>
            </div>

            <div class="space-y-5">
              <div v-for="nivel in arbolModulos" :key="nivel.label" class="rounded-2xl border border-[#ececec] bg-[#fafafa] p-4">
                <div class="mb-3 font-black uppercase tracking-[0.18em] text-[#575756] text-[11px]">{{ nivel.label }}</div>
                <div class="grid gap-3 sm:grid-cols-2">
                  <button
                    v-for="mod in nivel.items"
                    :key="mod.clave"
                    @click="navegarModulo(mod.clave)"
                    class="group flex w-full items-center justify-between rounded-2xl border px-3 py-3 text-left transition-all duration-200"
                    :class="moduloActivo === mod.clave ? 'border-[#575756] bg-[#f5f5f5] shadow-[0_8px_18px_rgba(87,87,86,0.08)]' : 'border-[#e8e8e8] bg-white hover:border-[#878787] hover:bg-[#fafafa]'"
                  >
                    <span class="font-semibold text-sm text-[#2f2f2f]">{{ mod.titulo }}</span>
                    <span
                      class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase"
                      :class="estadoModulos[mod.clave] ? 'bg-[#dfeee0] text-[#2d6d37]' : 'bg-[#ececec] text-[#575756]'"
                    >
                      {{ estadoModulos[mod.clave] ? "Listo" : "Pendiente" }}
                    </span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section v-else class="mx-auto max-w-5xl rounded-[28px] border border-[#d7d7d7] bg-white shadow-[0_18px_40px_rgba(87,87,86,0.08)] p-5">
        <div class="mb-5 flex items-center justify-between border-b border-[#e7e7e7] pb-3">
          <div>
            <p class="text-[10px] uppercase tracking-[0.25em] text-[#878787]">Módulo activo</p>
            <h2 class="text-xl font-black text-[#575756] mt-1">{{ moduloActual?.titulo || 'Módulo' }}</h2>
          </div>
          <button
            @click="volverAlArbol"
            class="rounded-full border border-[#d9d9d9] bg-[#f7f7f7] px-3 py-1.5 text-sm font-bold text-[#575756] hover:border-[#878787]"
          >
            Volver al árbol
          </button>
        </div>

        <component
          :is="componenteActivo"
          v-if="componenteActivo"
          :iph-id="iphId"
          :tipo="moduloActivo"
          @guardado="recargarEstado"
        />
        <div v-else class="bg-white rounded-lg shadow p-6 text-center text-gray-400">
          Este módulo está en construcción.
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../store/api";

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

const props = defineProps({
  id: { type: [String, Number], required: true },
  modulo: { type: String, default: null },
});

const router = useRouter();
const iphId = computed(() => props.id);

const iph = ref(null);
const estadoModulos = ref({});
const exportando = ref(false);

const moduloActivo = computed(() => props.modulo || null);

const componentesPorModulo = {
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
};

const componenteActivo = computed(() => (moduloActivo.value ? componentesPorModulo[moduloActivo.value] || null : null));
const moduloActual = computed(() => modulos.find((mod) => mod.clave === moduloActivo.value) || null);

const modulos = [
  { clave: "conocimiento_hecho", titulo: "Conocimiento de Hecho", descripcion: "Registro de la noticia" },
  { clave: "acta_noticia", titulo: "Acta de Noticia", descripcion: "Acta de noticia del hecho" },
  { clave: "acciones_realizadas", titulo: "Acciones Realizadas", descripcion: "Acciones realizadas" },
  { clave: "denunciante", titulo: "Denunciante", descripcion: "Datos del denunciante" },
  { clave: "ofendido", titulo: "Ofendido", descripcion: "Datos del ofendido" },
  { clave: "victima", titulo: "Víctima", descripcion: "Datos de la víctima" },
  { clave: "policias", titulo: "Policías", descripcion: "Policías actuantes" },
  { clave: "imputado", titulo: "Imputado", descripcion: "Datos del imputado" },
  { clave: "testigo", titulo: "Testigo", descripcion: "Testigos del hecho" },
  { clave: "inspeccion_lugar", titulo: "Inspección de Lugar", descripcion: "Inspección del lugar" },
  { clave: "inspeccion_persona", titulo: "Inspección de Persona", descripcion: "Inspección de persona" },
  { clave: "inspeccion_vehiculos", titulo: "Inspección de Vehículos", descripcion: "Inspección de vehículos" },
  { clave: "narracion_primer_respondiente", titulo: "Narración del Primer Respondiente", descripcion: "Narración de la actuación" },
  { clave: "actuaciones", titulo: "Actuaciones", descripcion: "Actuaciones realizadas" },
];

const arbolModulos = [
  { label: "Etapa 1", items: modulos.slice(0, 4) },
  { label: "Etapa 2", items: modulos.slice(4, 9) },
  { label: "Etapa 3", items: modulos.slice(9) },
];

const modulosCompletados = computed(() => Object.values(estadoModulos.value).filter(Boolean).length);

async function cargarIPH() {
  const { data } = await api.get(`/iph/${iphId.value}`);
  iph.value = data;
  estadoModulos.value = data.estado_modulos || {};
}

function recargarEstado() {
  cargarIPH();
}

function navegarModulo(clave) {
  router.push({
    name: "formulario-iph",
    params: { id: iphId.value, modulo: clave },
  });
}

function volverAlArbol() {
  router.push({
    name: "formulario-iph",
    params: { id: iphId.value },
  });
}

async function exportarPDF() {
  exportando.value = true;
  try {
    const response = await api.get(`/iph/${iphId.value}/exportar-pdf`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `IPH_${iph.value?.folio_interno}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } finally {
    exportando.value = false;
  }
}

onMounted(cargarIPH);
</script>

