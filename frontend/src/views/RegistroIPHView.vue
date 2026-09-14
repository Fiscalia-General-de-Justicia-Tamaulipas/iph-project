<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-[#1f2d3d] text-white px-6 py-4">
      <div class="max-w-6xl mx-auto flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div class="space-y-1">
          <p class="text-sm text-gray-300">{{ adscripcion }}</p>
          <p class="font-bold text-lg uppercase">{{ nombreUsuario }}</p>
        </div>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-200">{{ puesto }}</span>
          <button @click="$router.push({ name: 'panel' })" class="bg-[#d4af37] text-[#1f2d3d] px-3 py-1 rounded font-semibold hover:opacity-90">
            Volver al panel
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div class="mb-6">
          <div class="h-20 rounded-lg bg-gradient-to-r from-[#1f2d3d] to-[#2e7d32] flex items-center justify-center text-white text-2xl font-bold tracking-wide">
            IPH
          </div>
        </div>

        <div class="mb-6 flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="text-sm text-gray-500">Fecha</p>
            <p class="font-semibold text-gray-800">{{ fechaActual }}</p>
          </div>
          <button
            v-if="!iniciado"
            @click="iniciarNuc"
            class="bg-[#2e7d32] text-white px-5 py-2 rounded-md font-semibold hover:opacity-90"
          >
            INICIAR
          </button>
        </div>

        <div v-if="numeroNuc" class="mb-5">
          <p class="text-sm font-bold text-[#1f2d3d] uppercase">Número único de carpeta</p>
          <p class="text-2xl font-bold text-gray-900">{{ numeroNuc }}</p>
        </div>

        <div class="overflow-hidden rounded-md border border-gray-200">
          <div class="bg-gray-100 px-4 py-3 border-b border-gray-200 font-bold text-[#1f2d3d] uppercase">
            Árbol del IPH
          </div>

          <ul class="divide-y divide-gray-200">
            <li v-for="(nodo, index) in arbol" :key="nodo.label + index" class="px-4 py-3 bg-white">
              <div class="font-semibold text-gray-800">{{ nodo.label }}</div>

              <ul v-if="nodo.children && nodo.children.length" class="mt-2 ml-5 space-y-2">
                <li v-for="(hijo, hijoIndex) in nodo.children" :key="hijo.label + hijoIndex" class="text-sm text-gray-700">
                  <button
                    v-if="hijo.link"
                    @click="$router.push(hijo.link)"
                    class="text-left hover:text-[#2e7d32] hover:underline"
                  >
                    {{ hijo.label }}
                  </button>
                  <span v-else>{{ hijo.label }}</span>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useAuthStore } from "../store/auth";

const auth = useAuthStore();
const iniciado = ref(false);
const numeroNuc = ref("2026/000123");

const nombreUsuario = computed(() => auth.usuario?.nombre_completo || auth.usuario?.usuario || "USUARIO");
const adscripcion = computed(() => auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || "");
const puesto = computed(() => auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "");
const fechaActual = computed(() => new Date().toLocaleDateString("es-MX", {
  weekday: "long",
  day: "2-digit",
  month: "long",
  year: "numeric",
}));

const arbol = [
  {
    label: "IPH",
    children: [
      { label: "Conocimiento de hecho", link: { name: "formulario-iph", params: { id: 1 } } },
      { label: "Acta de noticia del hecho" },
      { label: "Acciones realizadas" },
      { label: "Denunciante" },
      { label: "Ofendido" },
      { label: "Víctima" },
      { label: "Policías" },
      { label: "Imputado" },
      { label: "Testigo" },
      { label: "Inspección de lugar" },
      { label: "Inspección de persona" },
      { label: "Inspección de vehículos" },
      { label: "Narración de la actuación del primer respondiente" },
      { label: "Actuaciones" },
    ],
  },
];

function iniciarNuc() {
  iniciado.value = true;
  numeroNuc.value = "NÚMERO ÚNICO DE CARPETA " + new Date().getFullYear() + "/" + String(Math.floor(Math.random() * 9000) + 1000);
}
</script>
