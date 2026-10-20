<template>
  <div class="dashboard">
    <header class="dash-header">
      <div class="dash-brand"><img src="/logos/logo_fgjtam.png" alt="FGJ Tamaulipas" /><span class="brand-divider"></span><div><small>FGJ TAMAULIPAS</small><strong>Informe Policial Homologado</strong></div></div>
      <div class="dash-account"><span class="account-avatar">{{ iniciales }}</span><div class="account-copy"><strong>{{ nombreUsuario }}</strong><small>{{ adscripcion || puesto || 'Personal autorizado' }}</small></div><button class="logout-button" @click="cerrarSesion" aria-label="Cerrar sesión" title="Cerrar sesión">↪</button></div>
    </header>

    <main class="dash-main">
      <div class="page-intro"><div><div class="breadcrumb">ESCRITORIO <span>/</span> REGISTROS</div><h1>Registros IPH</h1><p>Consulta y administra los informes policiales homologados.</p></div><div class="intro-date"><span class="date-icon">▦</span><span>{{ fechaActual }}</span></div></div>

      <section class="metric-grid" aria-label="Resumen de registros">
        <article class="metric-card"><span class="metric-icon icon-total">▤</span><div><small>Total de registros</small><strong>{{ totalRegistros }}</strong></div><span class="metric-note">REGISTROS</span></article>
        <article class="metric-card"><span class="metric-icon icon-active">✓</span><div><small>Activas</small><strong>{{ iphsActivas }}</strong></div><span class="metric-note">VIGENTES</span></article>
        <article class="metric-card"><span class="metric-icon icon-done">⌑</span><div><small>Terminadas</small><strong>{{ iphsTerminadas }}</strong></div><span class="metric-note">CONCLUIDAS</span></article>
        <article class="metric-card"><span class="metric-icon icon-pending">◷</span><div><small>Pendientes</small><strong>{{ iphsPendientes }}</strong></div><span class="metric-note">EN REVISIÓN</span></article>
      </section>

      <section class="records-panel">
        <div class="records-heading"><div><h2>Listado de informes</h2><p>Busca, ordena y consulta los registros disponibles.</p></div><div class="record-actions"><button class="secondary-action" @click="crearIPHConCarpeta"><span>＋</span> Carpeta existente</button><button class="primary-action" @click="crearIPH"><span>＋</span> Nuevo IPH</button></div></div>
        <div class="table-toolbar"><label class="search-box"><span aria-hidden="true">⌕</span><input v-model="busquedaGlobal" type="search" aria-label="Buscar registros" placeholder="Buscar por folio, NUC, persona o unidad…" /><kbd>⌘ K</kbd></label><label class="page-size">Mostrar <select v-model.number="registrosPorPagina" aria-label="Registros por página"><option :value="10">10</option><option :value="25">25</option><option :value="50">50</option></select></label></div>

        <div v-if="cargandoLista" class="table-state"><span class="spinner spinner-dark"></span><span>Cargando registros…</span></div>
        <div v-else-if="errorCarga" class="table-state state-error" role="alert"><span>!</span><div>{{ errorCarga }}<button @click="cargarIPH">Intentar de nuevo</button></div></div>
        <template v-else>
          <div class="table-scroll"><table class="records-table"><thead><tr><th><button class="sort-button" @click="ordenarPor('folio')">Folio interno <span>{{ iconoOrden('folio') }}</span></button></th><th><button class="sort-button" @click="ordenarPor('fecha')">Fecha de inicio <span>{{ iconoOrden('fecha') }}</span></button></th><th><button class="sort-button" @click="ordenarPor('denunciante')">Denunciante <span>{{ iconoOrden('denunciante') }}</span></button></th><th><button class="sort-button" @click="ordenarPor('imputado')">Imputado <span>{{ iconoOrden('imputado') }}</span></button></th><th><button class="sort-button" @click="ordenarPor('nuc')">NUC <span>{{ iconoOrden('nuc') }}</span></button></th><th>Unidad</th><th>Estado</th><th><span class="sr-only">Acciones</span></th></tr></thead>
            <tbody><tr v-for="iph in resultadosPaginados" :key="iph.id || iph.ID_IPH"><td><span class="folio-mark">▤</span><strong>{{ folio(iph) }}</strong></td><td>{{ formatearFecha(iph.creado_en || iph.FECHA_IPH) }}</td><td>{{ iph.denunciante || iph.DENUNCIANTE || '—' }}</td><td>{{ iph.imputado || iph.IMPUTADO || '—' }}</td><td class="nuc-cell">{{ iph.no_expediente || iph.NUC || '—' }}</td><td>{{ iph.adscripcion || iph.UNIDAD || '—' }}</td><td><span class="status-pill" :class="'status-' + clasificarEstado(iph)"><i></i>{{ textoEstado(iph) }}</span></td><td><button class="row-action" title="Ver informe" :aria-label="`Ver informe ${folio(iph)}`" @click="verIPH(iph)">↗</button></td></tr>
              <tr v-if="!resultadosPaginados.length"><td colspan="8" class="empty-cell"><span>⌕</span><strong>No se encontraron registros</strong><small>Prueba con otro término de búsqueda.</small></td></tr></tbody></table></div>
          <div class="mobile-records"><article v-for="iph in resultadosPaginados" :key="`mobile-${iph.id || iph.ID_IPH}`" class="mobile-record"><div class="mobile-record-top"><div><small>FOLIO INTERNO</small><strong>{{ folio(iph) }}</strong></div><span class="status-pill" :class="'status-' + clasificarEstado(iph)"><i></i>{{ textoEstado(iph) }}</span></div><div class="mobile-record-grid"><div><small>FECHA DE INICIO</small><span>{{ formatearFecha(iph.creado_en || iph.FECHA_IPH) }}</span></div><div><small>NUC</small><span>{{ iph.no_expediente || iph.NUC || '—' }}</span></div><div><small>DENUNCIANTE</small><span>{{ iph.denunciante || iph.DENUNCIANTE || '—' }}</span></div><div><small>IMPUTADO</small><span>{{ iph.imputado || iph.IMPUTADO || '—' }}</span></div><div class="mobile-unit"><small>UNIDAD</small><span>{{ iph.adscripcion || iph.UNIDAD || '—' }}</span></div></div><button class="mobile-view" @click="verIPH(iph)">Ver informe <span>→</span></button></article><div v-if="!resultadosPaginados.length" class="mobile-empty">No se encontraron registros.</div></div>
          <div class="table-footer"><p>Mostrando <strong>{{ resultados.length ? (paginaActual - 1) * registrosPorPagina + 1 : 0 }}–{{ Math.min(paginaActual * registrosPorPagina, resultados.length) }}</strong> de <strong>{{ resultados.length }}</strong> registros</p><nav v-if="totalPaginas > 1" class="pagination" aria-label="Paginación"><button aria-label="Página anterior" :disabled="paginaActual === 1" @click="paginaActual--">‹</button><span>Página <strong>{{ paginaActual }}</strong> de {{ totalPaginas }}</span><button aria-label="Página siguiente" :disabled="paginaActual === totalPaginas" @click="paginaActual++">›</button></nav></div>
        </template>
      </section>
      <footer class="dash-footer"><span>Sistema institucional de gestión IPH</span><span>Actualizado {{ horaActualizacion }}</span></footer>
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
const cargandoLista = ref(true);
const busquedaGlobal = ref("");
const registrosPorPagina = ref(10);
const paginaActual = ref(1);
const orden = ref({ campo: "fecha", direccion: "desc" });
const horaActualizacion = ref("—");
const nombreUsuario = computed(() => auth.usuario?.nombre_completo || auth.usuario?.usuario || "Usuario");
const adscripcion = computed(() => auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || auth.usuario?.undd_dscrpcion || "");
const puesto = computed(() => auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "");
const iniciales = computed(() => nombreUsuario.value.split(/\s+/).slice(0, 2).map((parte) => parte[0]).join("").toUpperCase());
const fechaActual = computed(() => new Date().toLocaleDateString("es-MX", { weekday: "long", day: "2-digit", month: "long", year: "numeric" }));
const totalRegistros = computed(() => listaIPH.value.length);
const iphsActivas = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "activa").length);
const iphsTerminadas = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "terminada").length);
const iphsPendientes = computed(() => listaIPH.value.filter((iph) => clasificarEstado(iph) === "pendiente").length);

function folio(iph) { return iph.folio_interno || iph.IPH || "Sin folio"; }
function textoEstado(iph) { const estado = iph.estado ?? iph.ESTADO_CARPETA ?? iph.ESTADO ?? iph.ESTADO_IPH ?? ""; return estado === "" ? "Sin estado" : String(estado); }
function clasificarEstado(iph) {
  const estado = textoEstado(iph).normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim().toUpperCase().replace(/[\s-]+/g, "_");
  if (["ACTIVA", "ACTIVO", "VIGENTE", "VIGENTES"].includes(estado)) return "activa";
  if (["TERMINADA", "TERMINADO", "COMPLETADA", "COMPLETADO", "COMPLETA", "COMPLETO", "CONCLUIDA", "CONCLUIDO", "FINALIZADA", "FINALIZADO", "CERRADA", "CERRADO"].includes(estado)) return "terminada";
  if (["PENDIENTE", "PENDIENTES", "EN_TRAMITE", "TRAMITE", "EN_PROCESO", "EN_CAPTURA", "CAPTURA", "POR_REVISAR"].includes(estado)) return "pendiente";
  return "sin-clasificar";
}
function formatearFecha(valor) { if (!valor) return "—"; const fecha = new Date(valor); return Number.isNaN(fecha.getTime()) ? valor : fecha.toLocaleDateString("es-MX", { day: "2-digit", month: "short", year: "numeric" }); }
function normalizar(valor) { return String(valor ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase(); }
const resultados = computed(() => {
  const termino = normalizar(busquedaGlobal.value.trim());
  const filtrados = listaIPH.value.filter((iph) => !termino || [folio(iph), iph.creado_en, iph.FECHA_IPH, iph.denunciante, iph.DENUNCIANTE, iph.imputado, iph.IMPUTADO, iph.no_expediente, iph.NUC, iph.adscripcion, iph.UNIDAD, textoEstado(iph)].some((valor) => normalizar(valor).includes(termino)));
  return filtrados.sort((a, b) => {
    const campo = orden.value.campo;
    const valores = { folio: [folio(a), folio(b)], fecha: [a.creado_en || a.FECHA_IPH || "", b.creado_en || b.FECHA_IPH || ""], denunciante: [a.denunciante || a.DENUNCIANTE || "", b.denunciante || b.DENUNCIANTE || ""], imputado: [a.imputado || a.IMPUTADO || "", b.imputado || b.IMPUTADO || ""], nuc: [a.no_expediente || a.NUC || "", b.no_expediente || b.NUC || ""] }[campo];
    const comparacion = normalizar(valores[0]).localeCompare(normalizar(valores[1]), "es", { numeric: true });
    return orden.value.direccion === "asc" ? comparacion : -comparacion;
  });
});
const totalPaginas = computed(() => Math.max(1, Math.ceil(resultados.value.length / registrosPorPagina.value)));
const resultadosPaginados = computed(() => resultados.value.slice((paginaActual.value - 1) * registrosPorPagina.value, paginaActual.value * registrosPorPagina.value));
watch([busquedaGlobal, registrosPorPagina], () => { paginaActual.value = 1; });
watch(totalPaginas, (total) => { if (paginaActual.value > total) paginaActual.value = total; });
function ordenarPor(campo) { orden.value = { campo, direccion: orden.value.campo === campo && orden.value.direccion === "asc" ? "desc" : "asc" }; }
function iconoOrden(campo) { return orden.value.campo !== campo ? "↕" : orden.value.direccion === "asc" ? "↑" : "↓"; }
function verIPH(iph) { router.push({ name: "formulario-iph", params: { id: iph.id || iph.ID_IPH } }); }
async function cargarIPH() {
  errorCarga.value = ""; cargandoLista.value = true;
  try { const { data } = await api.get("/iph/"); if (!Array.isArray(data)) throw new Error(data?.msg || "La respuesta del servidor no tiene el formato esperado."); listaIPH.value = data; horaActualizacion.value = new Date().toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }); }
  catch (error) { console.error("No fue posible cargar IPH:", error); listaIPH.value = []; errorCarga.value = error.response?.data?.msg || error.message || "No fue posible cargar los IPH."; }
  finally { cargandoLista.value = false; }
}
async function crearIPH() {
  try {
    if (!auth.usuario?.id_municipio && !auth.usuario?.IdMunicipio && !auth.usuario?.id_unidad && !auth.usuario?.IdUnidad) await auth.sincronizarUsuario();
    const payload = { municipio: auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? null, unidad: auth.usuario?.id_unidad ?? auth.usuario?.IdUnidad ?? null };
    if (payload.municipio == null || payload.unidad == null) throw new Error("La sesión actual no tiene municipio o unidad asociados.");
    const { data } = await api.post("/iph/", payload); const idIph = data.id || data.ID_IPH;
    await router.push({ name: "formulario-iph", params: { id: idIph }, query: { ID_IPH: idIph ?? "", ID_CARPETA: data.id_carpeta || 0, ESTADO_CARPETA: data.estado_carpeta || "TRAMITE", folio_interno: data.folio_interno || data.IPH || "" } });
  } catch (error) { console.error("No se pudo crear el IPH:", error); window.alert(error.response?.data?.msg || error.message || "No se pudo generar el IPH en la base de datos principal."); }
}
function crearIPHConCarpeta() { window.alert("La pantalla de carpeta existente se integra en la siguiente fase del módulo."); }
function cerrarSesion() { auth.cerrarSesion(); window.location.href = "/login"; }
onMounted(cargarIPH);
</script>
