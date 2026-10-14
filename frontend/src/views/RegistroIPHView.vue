<template>
  <div class="registro-view min-h-screen bg-[#efefef]">
    <header class="bg-[#575756] text-white shadow-sm border-b border-[#434342]">
      <div class="max-w-7xl mx-auto px-4 py-4 md:px-6">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div class="flex items-center gap-4">
            <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" class="h-14 w-auto rounded-lg bg-white/90 p-2 shadow-sm" />
            <div>
              <p class="text-[10px] uppercase tracking-[0.3em] text-[#dadada]">FGJ Tamaulipas</p>
              <h1 class="text-xl font-black tracking-wide">Registro del IPH</h1>
            </div>
          </div>

          <div class="flex items-center gap-3">
            <div class="text-right">
              <p class="text-xs uppercase tracking-wide text-[#dadada]">{{ adscripcion || 'Unidad' }}</p>
              <p class="text-sm font-semibold">{{ nombreUsuario }}</p>
            </div>
            <button @click="$router.push({ name: 'panel' })" class="rounded-xl bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10">
              Volver al panel
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-6 md:px-6">
      <section class="mb-6 rounded-2xl border border-[#d9d9d9] bg-white p-5 shadow-sm">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.25em] text-[#878787]">Fecha</p>
            <p class="mt-2 text-lg font-semibold text-[#1f1f1e]">{{ fechaActual }}</p>
          </div>

          <div class="flex items-center gap-3">
            <div class="rounded-xl bg-[#f5f5f5] px-4 py-3">
              <p class="text-[10px] uppercase tracking-[0.2em] text-[#575756]">Folio</p>
              <p class="text-lg font-black text-[#1f1f1e]">{{ numeroNuc || 'Sin folio' }}</p>
            </div>
            <button
              v-if="!iniciado"
              @click="iniciarNuc"
              class="rounded-xl bg-[#575756] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#454544]"
            >
              INICIAR
            </button>
          </div>
        </div>
      </section>

      <section class="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
        <aside class="rounded-2xl border border-[#d9d9d9] bg-white shadow-sm overflow-hidden">
          <div class="bg-[#575756] px-4 py-3 text-sm font-bold uppercase tracking-[0.2em] text-white">Árbol del IPH</div>

          <div class="p-4">
            <ul class="space-y-4">
              <li v-for="grupo in arbol" :key="grupo.label" class="tree-node">
                <div class="tree-branch font-black uppercase tracking-[0.18em] text-[#575756]">{{ grupo.label }}</div>
                <ul class="mt-3 space-y-2 pl-3 border-l border-[#e6e6e6]">
                  <li v-for="(hijo, index) in grupo.children" :key="hijo.label + index">
                    <button
                      v-if="hijo.link"
                      @click="$router.push(hijo.link)"
                      class="group flex w-full items-center justify-between rounded-xl border border-[#e0e0e0] bg-[#fafafa] px-3 py-2 text-left transition hover:border-[#878787] hover:bg-[#f2f2f2]"
                    >
                      <span class="text-sm font-medium text-[#2f2f2f]">{{ hijo.label }}</span>
                      <span class="rounded-full bg-[#ececec] px-2 py-0.5 text-[9px] font-bold uppercase text-[#575756]">Abrir</span>
                    </button>
                    <div v-else class="rounded-xl border border-dashed border-[#d7d7d7] bg-[#f9f9f9] px-3 py-2 text-sm text-[#575756] opacity-80">
                      {{ hijo.label }}
                    </div>
                  </li>
                </ul>
              </li>
            </ul>
          </div>
        </aside>

        <section class="rounded-2xl border border-[#d9d9d9] bg-white p-5 shadow-sm">
          <div class="mb-4 flex items-center justify-between border-b border-[#ececec] pb-3">
            <h2 class="text-xl font-black text-[#575756]">Resumen operativo</h2>
            <span class="rounded-full bg-[#eeeeee] px-2.5 py-1 text-[10px] font-bold uppercase tracking-[0.2em] text-[#575756]">IPH</span>
          </div>

          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div class="rounded-xl bg-[#f7f7f7] p-4 border border-[#e6e6e6]">
              <p class="text-[10px] uppercase tracking-[0.2em] text-[#878787]">Conocimiento</p>
              <p class="mt-2 text-lg font-bold text-[#1f1f1e]">Hecho y noticia</p>
            </div>
            <div class="rounded-xl bg-[#f7f7f7] p-4 border border-[#e6e6e6]">
              <p class="text-[10px] uppercase tracking-[0.2em] text-[#878787]">Investigación</p>
              <p class="mt-2 text-lg font-bold text-[#1f1f1e]">Lugar, persona y vehículo</p>
            </div>
            <div class="rounded-xl bg-[#f7f7f7] p-4 border border-[#e6e6e6]">
              <p class="text-[10px] uppercase tracking-[0.2em] text-[#878787]">Actuación</p>
              <p class="mt-2 text-lg font-bold text-[#1f1f1e]">Narrativa y actuaciones</p>
            </div>
          </div>
        </section>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "../store/auth";

const route = useRoute();
const auth = useAuthStore();
const iniciado = ref(false);
const numeroNuc = ref("");

function sincronizarNumeroNuc() {
  numeroNuc.value = route.query?.folio_interno || route.query?.IPH || route.query?.numero_carpeta || "2026/000123";
}

watch(() => route.query, sincronizarNumeroNuc, { immediate: true, deep: true });

const nombreUsuario = computed(() => auth.usuario?.nombre_completo || auth.usuario?.usuario || "USUARIO");
const adscripcion = computed(() => auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || "");
const puesto = computed(() => auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "");
const fechaActual = computed(() => new Date().toLocaleDateString("es-MX", {
  weekday: "long",
  day: "2-digit",
  month: "long",
  year: "numeric",
}));

const currentIphId = computed(() => Number(route.query?.ID_IPH || route.params?.id || 1) || 1);

const arbol = computed(() => [
  {
    label: "Hechos iniciales",
    children: [
      { label: "Conocimiento de hecho", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "conocimiento_hecho" } } },
      { label: "Acta de noticia del hecho", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "acta_noticia" } } },
      { label: "Acciones realizadas", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "acciones_realizadas" } } },
    ],
  },
  {
    label: "Personas y autoridades",
    children: [
      { label: "Denunciante", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "denunciante" } } },
      { label: "Ofendido", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "ofendido" } } },
      { label: "Víctima", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "victima" } } },
      { label: "Policías", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "policias" } } },
      { label: "Imputado", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "imputado" } } },
      { label: "Testigo", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "testigo" } } },
    ],
  },
  {
    label: "Inspección y narrativa",
    children: [
      { label: "Inspección de lugar", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "inspeccion_lugar" } } },
      { label: "Inspección de persona", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "inspeccion_persona" } } },
      { label: "Inspección de vehículos", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "inspeccion_vehiculos" } } },
      { label: "Narración del primer respondiente", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "narracion_primer_respondiente" } } },
      { label: "Actuaciones", link: { name: "formulario-iph", params: { id: currentIphId.value, modulo: "actuaciones" } } },
    ],
  },
]);

function iniciarNuc() {
  iniciado.value = true;
  numeroNuc.value = "NÚMERO ÚNICO DE CARPETA " + new Date().getFullYear() + "/" + String(Math.floor(Math.random() * 9000) + 1000);
}
</script>
