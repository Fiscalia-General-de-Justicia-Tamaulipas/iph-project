<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-institucional-oscuro text-white px-6 py-4">
      <div class="max-w-6xl mx-auto flex justify-between items-center">
        <div>
          <button @click="$router.push({ name: 'panel' })" class="text-xs text-gray-300 hover:underline">← Volver al panel</button>
          <h1 class="font-bold text-lg">IPH — Folio {{ iph?.folio_interno }}</h1>
        </div>
        <button
          @click="exportarPDF"
          :disabled="exportando"
          class="bg-institucional-dorado text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
        >
          {{ exportando ? "Generando..." : "Exportar a PDF" }}
        </button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto p-6">
      <!-- Vista de tarjetas (panel de módulos, igual al mockup) -->
      <div v-if="!moduloActivo" class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <button
          v-for="mod in modulos"
          :key="mod.clave"
          @click="moduloActivo = mod.clave"
          class="bg-white rounded-lg shadow p-4 text-left hover:shadow-md transition"
        >
          <p class="font-semibold text-gray-800">{{ mod.titulo }}</p>
          <p class="text-xs text-gray-500 mb-2">{{ mod.descripcion }}</p>
          <span
            class="text-xs px-2 py-1 rounded-full font-semibold"
            :class="estadoModulos[mod.clave] ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
          >
            {{ estadoModulos[mod.clave] ? "COMPLETADO" : "PENDIENTE" }}
          </span>
        </button>
      </div>

      <!-- Vista de un módulo específico -->
      <div v-else>
        <button @click="volverAPanelModulos" class="text-sm text-institucional-verde mb-4 hover:underline">
          ← Volver a los módulos
        </button>

        <component
          :is="componenteActivo"
          v-if="componenteActivo"
          :iph-id="iphId"
          @guardado="recargarEstado"
        />
        <div v-else class="bg-white rounded-lg shadow p-6 text-center text-gray-400">
          Este módulo está en construcción. Sigue el patrón de
          <code>ConocimientoHechoForm.vue</code> o <code>DenuncianteForm.vue</code>
          para implementarlo.
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../store/api";

import ConocimientoHechoForm from "./modulos/ConocimientoHechoForm.vue";
import DenuncianteForm from "./modulos/DenuncianteForm.vue";

const props = defineProps({ id: { type: [String, Number], required: true } });
const iphId = computed(() => props.id);

const iph = ref(null);
const estadoModulos = ref({});
const moduloActivo = ref(null);
const exportando = ref(false);

// Mapa de módulos -> componente Vue. Agrega aquí cada nuevo módulo conforme
// lo implementes, siguiendo el mismo patrón (props: iphId, emit: 'guardado').
const componentesPorModulo = {
  conocimiento_hecho: ConocimientoHechoForm,
  denunciante: DenuncianteForm,
};

const componenteActivo = computed(() => componentesPorModulo[moduloActivo.value] || null);

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

async function cargarIPH() {
  const { data } = await api.get(`/iph/${iphId.value}`);
  iph.value = data;
  estadoModulos.value = data.estado_modulos;
}

function volverAPanelModulos() {
  moduloActivo.value = null;
  cargarIPH();
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
