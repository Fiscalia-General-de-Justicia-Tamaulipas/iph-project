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
          <button @click="cerrarSesion" class="bg-[#d4af37] text-[#1f2d3d] px-3 py-1 rounded font-semibold hover:opacity-90">
            Cerrar sesión
          </button>
        </div>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6">
      <div class="mb-5 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-semibold text-gray-700">{{ fechaActual }}</span>
        </div>
        <div class="flex items-center gap-3">
          <button @click="crearIPH" class="bg-[#2e7d32] text-white px-5 py-2 rounded-md font-semibold hover:opacity-90">
            NUEVO IPH
          </button>
          <button @click="crearIPHConCarpeta" class="bg-[#2e7d32] text-white px-5 py-2 rounded-md font-semibold hover:opacity-90">
            CON CARPETA EXISTENTE
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-5">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-center">
          <label class="text-sm font-bold text-gray-700">BUSCAR</label>
          <select v-model="filtroBusqueda" class="border border-gray-300 rounded px-3 py-2 min-w-[220px]">
            <option value="0">POR:</option>
            <option value="1">IPH</option>
            <option value="2">FECHA INICIO IPH</option>
            <option value="3">NUC</option>
            <option value="4">DENUNCIANTE</option>
            <option value="5">IMPUTADO</option>
          </select>
        </div>

        <div class="mt-5 flex flex-wrap items-center justify-center gap-3">
          <template v-if="filtroBusqueda === '1'">
            <label class="font-bold text-sm text-gray-700">IPH</label>
            <input v-model="busqueda.iph" class="border border-gray-300 rounded px-3 py-2" placeholder="Escribe el IPH" />
          </template>

          <template v-else-if="filtroBusqueda === '2'">
            <label class="font-bold text-sm text-gray-700">FECHA INICIO</label>
            <input v-model="busqueda.fechaInicio" type="date" class="border border-gray-300 rounded px-3 py-2" />
            <label class="font-bold text-sm text-gray-700">FECHA FIN</label>
            <input v-model="busqueda.fechaFin" type="date" class="border border-gray-300 rounded px-3 py-2" />
          </template>

          <template v-else-if="filtroBusqueda === '3'">
            <label class="font-bold text-sm text-gray-700">NUC</label>
            <input v-model="busqueda.nuc" class="border border-gray-300 rounded px-3 py-2" placeholder="Ej. 123/2026" />
          </template>

          <template v-else-if="filtroBusqueda === '4'">
            <label class="font-bold text-sm text-gray-700">NOMBRE</label>
            <input v-model="busqueda.nombreDen" class="border border-gray-300 rounded px-3 py-2" />
            <label class="font-bold text-sm text-gray-700">PATERNO</label>
            <input v-model="busqueda.paternoDen" class="border border-gray-300 rounded px-3 py-2" />
            <label class="font-bold text-sm text-gray-700">MATERNO</label>
            <input v-model="busqueda.maternoDen" class="border border-gray-300 rounded px-3 py-2" />
          </template>

          <template v-else-if="filtroBusqueda === '5'">
            <label class="font-bold text-sm text-gray-700">NOMBRE</label>
            <input v-model="busqueda.nombreIm" class="border border-gray-300 rounded px-3 py-2" />
            <label class="font-bold text-sm text-gray-700">PATERNO</label>
            <input v-model="busqueda.paternoIm" class="border border-gray-300 rounded px-3 py-2" />
            <label class="font-bold text-sm text-gray-700">MATERNO</label>
            <input v-model="busqueda.maternoIm" class="border border-gray-300 rounded px-3 py-2" />
          </template>

          <button
            v-if="filtroBusqueda !== '0'"
            @click="ejecutarBusqueda"
            class="bg-[#2e7d32] text-white px-5 py-2 rounded-md font-semibold hover:opacity-90"
          >
            ACEPTAR
          </button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full text-left">
            <thead class="bg-[#87868B] text-white">
              <tr>
                <th class="px-4 py-3"> </th>
                <th class="px-4 py-3">FOLIO INTERNO</th>
                <th class="px-4 py-3">FECHA INICIO</th>
                <th class="px-4 py-3">DENUNCIANTE</th>
                <th class="px-4 py-3">IMPUTADO</th>
                <th class="px-4 py-3">NUC</th>
                <th class="px-4 py-3">UNIDAD</th>
                <th class="px-4 py-3">ESTADO CARPETA</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="iph in resultados" :key="iph.id || iph.ID_IPH" class="border-t border-gray-200 hover:bg-gray-50">
                <td class="px-4 py-3">
                  <button @click="$router.push({ name: 'formulario-iph', params: { id: iph.id || iph.ID_IPH } })" class="bg-white border border-gray-300 rounded p-1 hover:bg-gray-100">
                    <span class="text-lg">👁</span>
                  </button>
                </td>
                <td class="px-4 py-3 font-semibold text-gray-800">{{ iph.folio_interno || iph.IPH || "—" }}</td>
                <td class="px-4 py-3 text-gray-700">{{ formatearFecha(iph.creado_en || iph.FECHA_IPH) }}</td>
                <td class="px-4 py-3 text-gray-700">{{ iph.denunciante || iph.DENUNCIANTE || "—" }}</td>
                <td class="px-4 py-3 text-gray-700">{{ iph.imputado || iph.IMPUTADO || "—" }}</td>
                <td class="px-4 py-3 text-gray-700">{{ iph.no_expediente || iph.NUC || "—" }}</td>
                <td class="px-4 py-3 text-gray-700">{{ iph.adscripcion || iph.UNIDAD || "—" }}</td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex rounded-full px-2 py-1 text-xs font-semibold"
                    :class="(iph.estado || iph.ESTADO_CARPETA || 'EN_TRAMITE') === 'ACTIVA' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                  >
                    {{ iph.estado || iph.ESTADO_CARPETA || 'EN_TRAMITE' }}
                  </span>
                </td>
              </tr>
              <tr v-if="resultados.length === 0">
                <td colspan="8" class="px-4 py-8 text-center text-gray-500">No hay registros para mostrar.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";
import api from "../store/api";

const router = useRouter();
const auth = useAuthStore();
const listaIPH = ref([]);
const filtroBusqueda = ref("0");

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

async function cargarIPH() {
  try {
    const { data } = await api.get("/iph/");
    listaIPH.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error("No fue posible cargar IPH:", error);
    listaIPH.value = [];
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
      name: "registro-iph",
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
