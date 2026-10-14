<template>
  <div class="panel-view min-h-screen bg-[#efefef]">
    <header class="bg-[#575756] text-white shadow-sm border-b border-[#434342]">
      <div class="max-w-7xl mx-auto px-4 py-4 md:px-6">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex items-center gap-4">
            <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" class="h-14 w-auto rounded-lg bg-white/90 p-2 shadow-sm" />
            <div>
              <p class="text-[10px] uppercase tracking-[0.3em] text-[#dadada]">FGJ Tamaulipas</p>
              <h1 class="text-xl font-black tracking-wide">IPH - Informe Policial Homologado</h1>
            </div>
          </div>

          <div class="flex flex-col items-start gap-2 md:flex-row md:items-center">
            <div class="text-right">
              <p class="text-xs uppercase tracking-wide text-[#dadada]">{{ adscripcion || 'Unidad' }}</p>
              <p class="text-sm font-semibold">{{ nombreUsuario }}</p>
            </div>
            <button @click="cerrarSesion" class="rounded-xl border border-white/30 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10">
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 py-6 md:px-6">
      <section class="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm">
          <p class="text-xs uppercase tracking-[0.25em] text-[#878787]">Total</p>
          <div class="mt-3 flex items-end justify-between">
            <span class="text-3xl font-black text-[#575756]">{{ totalRegistros }}</span>
            <span class="rounded-full bg-[#ececec] px-2 py-1 text-[10px] font-bold uppercase text-[#575756]">IPH</span>
          </div>
        </div>
        <div class="rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm">
          <p class="text-xs uppercase tracking-[0.25em] text-[#878787]">Activas</p>
          <div class="mt-3 flex items-end justify-between">
            <span class="text-3xl font-black text-[#2d6d37]">{{ iphsActivas }}</span>
            <span class="rounded-full bg-[#dfeee0] px-2 py-1 text-[10px] font-bold uppercase text-[#2d6d37]">Vigentes</span>
          </div>
        </div>
        <div class="rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm">
          <p class="text-xs uppercase tracking-[0.25em] text-[#878787]">Terminadas</p>
          <div class="mt-3 flex items-end justify-between">
            <span class="text-3xl font-black text-[#575756]">{{ iphsTerminadas }}</span>
            <span class="rounded-full bg-[#ececec] px-2 py-1 text-[10px] font-bold uppercase text-[#575756]">Concluidas</span>
          </div>
        </div>
        <div class="rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm">
          <p class="text-xs uppercase tracking-[0.25em] text-[#878787]">Pendientes</p>
          <div class="mt-3 flex items-end justify-between">
            <span class="text-3xl font-black text-[#7a5c00]">{{ iphsPendientes }}</span>
            <span class="rounded-full bg-[#f7f0d7] px-2 py-1 text-[10px] font-bold uppercase text-[#7a5c00]">Por revisar</span>
          </div>
        </div>
      </section>

      <section class="rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm mb-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex items-center gap-3">
            <span class="text-sm font-semibold text-[#575756]">{{ fechaActual }}</span>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row">
            <button @click="crearIPH" class="rounded-xl bg-[#575756] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#454544]">
              NUEVO IPH
            </button>
            <button @click="crearIPHConCarpeta" class="rounded-xl bg-[#878787] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#737373]">
              CON CARPETA EXISTENTE
            </button>
          </div>
        </div>
      </section>

      <section class="mb-6 rounded-2xl border border-[#d9d9d9] bg-white p-4 shadow-sm">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <div class="flex items-center gap-3">
            <label class="text-sm font-bold uppercase tracking-[0.2em] text-[#575756]">Buscar</label>
            <select v-model="filtroBusqueda" class="min-w-[240px] rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5 text-sm text-[#1f1f1e] focus:border-[#878787] focus:outline-none">
              <option value="0">POR:</option>
              <option value="1">IPH</option>
              <option value="2">FECHA INICIO IPH</option>
              <option value="3">NUC</option>
              <option value="4">DENUNCIANTE</option>
              <option value="5">IMPUTADO</option>
            </select>
          </div>
        </div>

        <div class="mt-5 grid gap-3 xl:grid-cols-[repeat(auto-fit,minmax(180px,1fr))]">
          <template v-if="filtroBusqueda === '1'">
            <div class="xl:col-span-2">
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">IPH</label>
              <input v-model="busqueda.iph" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" placeholder="Escribe el IPH" />
            </div>
          </template>

          <template v-else-if="filtroBusqueda === '2'">
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Fecha inicio</label>
              <input v-model="busqueda.fechaInicio" type="date" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Fecha fin</label>
              <input v-model="busqueda.fechaFin" type="date" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
          </template>

          <template v-else-if="filtroBusqueda === '3'">
            <div class="xl:col-span-2">
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">NUC</label>
              <input v-model="busqueda.nuc" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" placeholder="Ej. 123/2026" />
            </div>
          </template>

          <template v-else-if="filtroBusqueda === '4'">
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Nombre</label>
              <input v-model="busqueda.nombreDen" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Paterno</label>
              <input v-model="busqueda.paternoDen" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Materno</label>
              <input v-model="busqueda.maternoDen" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
          </template>

          <template v-else-if="filtroBusqueda === '5'">
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Nombre</label>
              <input v-model="busqueda.nombreIm" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Paterno</label>
              <input v-model="busqueda.paternoIm" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
            <div>
              <label class="mb-2 block text-xs font-bold uppercase tracking-[0.2em] text-[#575756]">Materno</label>
              <input v-model="busqueda.maternoIm" class="w-full rounded-xl border border-[#d0d0d0] bg-[#fafafa] px-3 py-2.5" />
            </div>
          </template>

          <div v-if="filtroBusqueda !== '0'" class="flex items-end">
            <button @click="ejecutarBusqueda" class="w-full rounded-xl bg-[#575756] px-5 py-2.5 text-sm font-bold text-white transition hover:bg-[#454544]">
              ACEPTAR
            </button>
          </div>
        </div>
      </section>

      <section class="overflow-hidden rounded-2xl border border-[#d9d9d9] bg-white shadow-sm">
        <div class="overflow-x-auto">
          <table class="min-w-full text-left">
            <thead class="bg-[#878787] text-white">
              <tr>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]"> </th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Folio interno</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Fecha inicio</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Denunciante</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Imputado</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">NUC</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Unidad</th>
                <th class="px-4 py-3 text-xs uppercase tracking-[0.2em]">Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="iph in resultadosPaginados" :key="iph.id || iph.ID_IPH" class="border-t border-[#ececec] hover:bg-[#f9f9f9]">
                <td class="px-4 py-3">
                  <button @click="$router.push({ name: 'formulario-iph', params: { id: iph.id || iph.ID_IPH } })" class="rounded-lg border border-[#d0d0d0] bg-white px-2 py-1.5 text-base transition hover:border-[#575756] hover:bg-[#f0f0f0]">
                    👁
                  </button>
                </td>
                <td class="px-4 py-3 font-semibold text-[#1f1f1e]">{{ iph.folio_interno || iph.IPH || "—" }}</td>
                <td class="px-4 py-3 text-[#4d4d4d]">{{ formatearFecha(iph.creado_en || iph.FECHA_IPH) }}</td>
                <td class="px-4 py-3 text-[#4d4d4d]">{{ iph.denunciante || iph.DENUNCIANTE || "—" }}</td>
                <td class="px-4 py-3 text-[#4d4d4d]">{{ iph.imputado || iph.IMPUTADO || "—" }}</td>
                <td class="px-4 py-3 text-[#4d4d4d]">{{ iph.no_expediente || iph.NUC || "—" }}</td>
                <td class="px-4 py-3 text-[#4d4d4d]">{{ iph.adscripcion || iph.UNIDAD || "—" }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
                    :class="claseEstado(iph)"
                  >
                    {{ textoEstado(iph) }}
                  </span>
                </td>
              </tr>
              <tr v-if="errorCarga">
                <td colspan="8" class="px-4 py-10 text-center text-red-700">{{ errorCarga }}</td>
              </tr>
              <tr v-else-if="resultados.length === 0">
                <td colspan="8" class="px-4 py-10 text-center text-[#575756]">No hay registros para mostrar.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="flex flex-col gap-3 border-t border-[#ececec] px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <p class="text-sm text-[#575756]">
            Mostrando {{ resultados.length ? (paginaActual - 1) * registrosPorPagina + 1 : 0 }}–{{ Math.min(paginaActual * registrosPorPagina, resultados.length) }}
            de {{ resultados.length }} registros
          </p>
          <nav v-if="totalPaginas > 1" aria-label="Paginación de registros" class="flex items-center justify-center gap-2">
            <button
              type="button"
              @click="paginaActual--"
              :disabled="paginaActual === 1"
              class="rounded-lg border border-[#d0d0d0] bg-white px-3 py-2 text-sm font-semibold text-[#575756] disabled:cursor-not-allowed disabled:opacity-50"
            >
              Anterior
            </button>
            <span class="min-w-24 text-center text-sm font-semibold text-[#575756]">
              Página {{ paginaActual }} de {{ totalPaginas }}
            </span>
            <button
              type="button"
              @click="paginaActual++"
              :disabled="paginaActual === totalPaginas"
              class="rounded-lg border border-[#d0d0d0] bg-white px-3 py-2 text-sm font-semibold text-[#575756] disabled:cursor-not-allowed disabled:opacity-50"
            >
              Siguiente
            </button>
          </nav>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import api from "../store/api";

const router = useRouter();
const auth = useAuthStore();
const listaIPH = ref([]);
const errorCarga = ref("");
const filtroBusqueda = ref("0");
const registrosPorPagina = 10;
const paginaActual = ref(1);

const busqueda = ref({
  iph: "",
  fechaInicio: "",
  fechaFin: "",
  nuc: "",
  nombreDen: "",
  paternoDen: "",
  maternoDen: "",
  nombreIm: "",
  paternoIm: "",
  maternoIm: "",
});

const nombreUsuario = computed(() => auth.usuario?.nombre_completo || auth.usuario?.usuario || "USUARIO");
const adscripcion = computed(() => auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || auth.usuario?.undd_dscrpcion || "");
const puesto = computed(() => auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "");
const fechaActual = computed(() => new Date().toLocaleDateString("es-MX", {
  weekday: "long",
  day: "2-digit",
  month: "long",
  year: "numeric",
}));

const totalRegistros = computed(() => listaIPH.value.length);
const iphsActivas = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "activa").length);
const iphsTerminadas = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "terminada").length);
const iphsPendientes = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "pendiente").length);

function valorEstado(iph) {
  return iph.estado ?? iph.ESTADO_CARPETA ?? iph.ESTADO ?? iph.ESTADO_IPH ?? "";
}

function textoEstado(iph) {
  const estado = valorEstado(iph);
  return estado === "" ? "Sin estado" : String(estado);
}

function clasificarEstado(iph) {
  const estado = textoEstado(iph)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
    .toUpperCase()
    .replace(/[\s-]+/g, "_");

  if (["ACTIVA", "ACTIVO", "VIGENTE", "VIGENTES"].includes(estado)) return "activa";
  if (["TERMINADA", "TERMINADO", "COMPLETADA", "COMPLETADO", "COMPLETA", "COMPLETO", "CONCLUIDA", "CONCLUIDO", "FINALIZADA", "FINALIZADO", "CERRADA", "CERRADO"].includes(estado)) return "terminada";
  if (["PENDIENTE", "PENDIENTES", "EN_TRAMITE", "TRAMITE", "EN_PROCESO", "EN_CAPTURA", "CAPTURA", "POR_REVISAR"].includes(estado)) return "pendiente";
  return "sin-clasificar";
}

function claseEstado(iph) {
  const estado = clasificarEstado(iph);
  if (estado === "activa") return "bg-[#dfeee0] text-[#2d6d37]";
  if (estado === "terminada") return "bg-[#ececec] text-[#575756]";
  if (estado === "pendiente") return "bg-[#f7f0d7] text-[#7a5c00]";
  return "bg-[#ededed] text-[#575756]";
}

function formatearFecha(valor) {
  if (!valor) return "—";
  const fecha = new Date(valor);
  if (Number.isNaN(fecha.getTime())) return valor;
  return fecha.toLocaleDateString("es-MX", { day: "2-digit", month: "2-digit", year: "numeric" });
}

const resultados = computed(() => {
  const base = [...listaIPH.value];

  if (filtroBusqueda.value === "0") return base;

  return base.filter((iph) => {
    if (filtroBusqueda.value === "1") {
      const valor = (iph.folio_interno || iph.IPH || "").toLowerCase();
      return valor.includes((busqueda.value.iph || "").toLowerCase());
    }

    if (filtroBusqueda.value === "2") {
      const fecha = (iph.creado_en || iph.FECHA_IPH) ? new Date(iph.creado_en || iph.FECHA_IPH) : null;
      if (!fecha || Number.isNaN(fecha.getTime())) return false;
      const inicio = busqueda.value.fechaInicio ? new Date(busqueda.value.fechaInicio) : null;
      const fin = busqueda.value.fechaFin ? new Date(busqueda.value.fechaFin) : null;

      if (inicio && fin) return fecha >= inicio && fecha <= fin;
      if (inicio) return fecha >= inicio;
      if (fin) return fecha <= fin;
      return true;
    }

    if (filtroBusqueda.value === "3") {
      const valor = (iph.no_expediente || iph.NUC || "").toLowerCase();
      return valor.includes((busqueda.value.nuc || "").toLowerCase());
    }

    if (filtroBusqueda.value === "4") {
      const nombre = (iph.denunciante || iph.DENUNCIANTE || "").toLowerCase();
      return nombre.includes((busqueda.value.nombreDen || "").toLowerCase())
        && nombre.includes((busqueda.value.paternoDen || "").toLowerCase())
        && nombre.includes((busqueda.value.maternoDen || "").toLowerCase());
    }

    if (filtroBusqueda.value === "5") {
      const nombre = (iph.imputado || iph.IMPUTADO || "").toLowerCase();
      return nombre.includes((busqueda.value.nombreIm || "").toLowerCase())
        && nombre.includes((busqueda.value.paternoIm || "").toLowerCase())
        && nombre.includes((busqueda.value.maternoIm || "").toLowerCase());
    }

    return true;
  });
});

const totalPaginas = computed(() => Math.max(1, Math.ceil(resultados.value.length / registrosPorPagina)));
const resultadosPaginados = computed(() => {
  const inicio = (paginaActual.value - 1) * registrosPorPagina;
  return resultados.value.slice(inicio, inicio + registrosPorPagina);
});

watch(resultados, () => {
  paginaActual.value = 1;
});

watch(totalPaginas, (total) => {
  if (paginaActual.value > total) paginaActual.value = total;
});

async function cargarIPH() {
  errorCarga.value = "";
  try {
    const { data } = await api.get("/iph/");
    if (!Array.isArray(data)) {
      throw new Error(data?.msg || "La respuesta del servidor no tiene el formato esperado.");
    }
    listaIPH.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("No fue posible cargar IPH:", error);
    listaIPH.value = [];
    errorCarga.value = error.response?.data?.msg || error.message || "No fue posible cargar los IPH.";
  }
}

async function crearIPH() {
  try {
    if (!auth.usuario?.id_municipio && !auth.usuario?.IdMunicipio && !auth.usuario?.id_unidad && !auth.usuario?.IdUnidad) {
      await auth.sincronizarUsuario();
    }

    const payload = {
      municipio: auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? null,
      unidad: auth.usuario?.id_unidad ?? auth.usuario?.IdUnidad ?? null,
    };

    if (payload.municipio == null || payload.unidad == null) {
      throw new Error("La sesión actual no tiene municipio o unidad asociados.");
    }

    const { data } = await api.post("/iph/", payload);
    const idIph = data.id || data.ID_IPH;
    const folio = data.folio_interno || data.IPH || "";

    await router.push({
      name: "formulario-iph",
      params: { id: idIph },
      query: {
        ID_IPH: idIph ?? "",
        ID_CARPETA: data.id_carpeta || 0,
        ESTADO_CARPETA: data.estado_carpeta || "TRAMITE",
        folio_interno: folio,
      },
    });
  } catch (error) {
    console.error("No se pudo crear el IPH:", error);
    window.alert(error.response?.data?.msg || error.message || "No se pudo generar el IPH en la base de datos principal.");
  }
}

function crearIPHConCarpeta() {
  window.alert("La pantalla de carpeta existente se integra en la siguiente fase del módulo.");
}

function ejecutarBusqueda() {
  return true;
}

function cerrarSesion() {
  auth.cerrarSesion();
  window.location.href = "/login";
}

onMounted(cargarIPH);
</script>
