<template>
  <div class="inspeccion-lugar-form">
    <form @submit.prevent="guardar">
      <section class="inspeccion-lugar-block" aria-labelledby="ubicacion-heading">
        <h2 id="ubicacion-heading" class="inspeccion-lugar-subheading">
          Apartado 4.1 Ubicación geográfica
        </h2>

        <div class="inspeccion-lugar-section-content">
          <fieldset class="ubicacion-modos">
            <legend class="sr-only">Método para registrar la ubicación</legend>
            <label>
              <input v-model="modoUbicacion" type="radio" value="punteo" />
              <span>Datos Geográficos del Punteo</span>
            </label>
            <label>
              <input v-model="modoUbicacion" type="radio" value="georreferenciacion" />
              <span>Georreferenciación</span>
            </label>
            <button type="button" class="map-picker-trigger" @click="abrirMapa" aria-haspopup="dialog" aria-label="Abrir mapa para seleccionar la georreferenciación">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.1 7-12a7 7 0 1 0-14 0c0 5.9 7 12 7 12Z"/><circle cx="12" cy="9" r="2.2"/></svg>
              <span>Elegir en mapa</span>
            </button>
          </fieldset>

          <div class="ubicacion-coordenadas">
            <p class="ubicacion-ayuda">
              {{
                modoUbicacion === "punteo"
                  ? "Registre las coordenadas del punto de intervención."
                  : "Anote las coordenadas geográficas del lugar."
              }}
            </p>
            <div class="inspeccion-lugar-grid coordenadas-grid">
              <div class="inspeccion-lugar-field">
                <label for="lugar-latitud">Latitud</label>
                <input
                  id="lugar-latitud"
                  v-model="form.latitud"
                  type="text"
                  inputmode="decimal"
                  autocomplete="off"
                />
              </div>
              <div class="inspeccion-lugar-field">
                <label for="lugar-longitud">Longitud</label>
                <input
                  id="lugar-longitud"
                  v-model="form.longitud"
                  type="text"
                  inputmode="decimal"
                  autocomplete="off"
                />
              </div>
              <div class="coordenadas-accion">
                <a
                  v-if="mapaHref"
                  :href="mapaHref"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inspeccion-lugar-map-link"
                >
                  Ver punto en mapa
                </a>
                <span v-else class="inspeccion-lugar-map-hint">Capture las coordenadas para ver el mapa.</span>
              </div>
            </div>
          </div>

          <h3 class="inspeccion-lugar-minor-heading">Datos geográficos</h3>
          <div class="inspeccion-lugar-grid datos-geograficos-grid">
            <div class="inspeccion-lugar-field field-span-2">
              <label for="lugar-calle">Calle / tramo carretero</label>
              <input id="lugar-calle" v-model="form.calle" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-no-exterior">No. exterior</label>
              <input id="lugar-no-exterior" v-model="form.no_exterior" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-municipio">Municipio / demarcación territorial</label>
              <input id="lugar-municipio" v-model="form.municipio" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-localidad">Localidad</label>
              <input id="lugar-localidad" v-model="form.localidad" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-colonia">Colonia / localidad</label>
              <input id="lugar-colonia" v-model="form.colonia" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-entre-calle">Entre calle</label>
              <input id="lugar-entre-calle" v-model="form.entre_calle" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-y-calle">Y calle</label>
              <input id="lugar-y-calle" v-model="form.y_calle" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-brecha">Brecha</label>
              <input id="lugar-brecha" v-model="form.brecha" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-kilometro">Kilómetro</label>
              <input id="lugar-kilometro" v-model="form.kilometro" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-manzana">Manzana</label>
              <input id="lugar-manzana" v-model="form.manzana" type="text" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-lote">Lote</label>
              <input id="lugar-lote" v-model="form.lote" type="text" />
            </div>
          </div>

          <div class="inspeccion-lugar-field referencias-field">
            <label for="lugar-referencias">Referencias*</label>
            <textarea id="lugar-referencias" v-model="form.referencias" rows="3"></textarea>
          </div>

          <h3 class="inspeccion-lugar-minor-heading">Datos del lugar</h3>
          <div class="inspeccion-lugar-grid datos-lugar-grid">
            <div class="inspeccion-lugar-field">
              <label for="lugar-fecha">Fecha de inspección</label>
              <input id="lugar-fecha" v-model="form.fecha_inspeccion" type="date" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-hora">Hora</label>
              <input id="lugar-hora" v-model="form.hora_inspeccion" type="time" />
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-tipo">Tipo de lugar</label>
              <select id="lugar-tipo" v-model="form.tipo_lugar">
                <option value="">--SELECCIONE--</option>
                <option value="VIVIENDA">VIVIENDA</option>
                <option value="CALLE">CALLE</option>
                <option value="PREDIO">PREDIO</option>
                <option value="NEGOCIO">NEGOCIO</option>
                <option value="VEHICULO">VEHÍCULO</option>
                <option value="OTRO">OTRO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-tipo-suelo">Tipo de suelo</label>
              <select id="lugar-tipo-suelo" v-model="form.tipo_suelo">
                <option value="">--SELECCIONE--</option>
                <option value="ARENOSO">ARENOSO</option>
                <option value="ARCILLOSO">ARCILLOSO</option>
                <option value="PEDREGOSO">PEDREGOSO</option>
                <option value="OTRO">OTRO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-condiciones-suelo">Condiciones del suelo</label>
              <select id="lugar-condiciones-suelo" v-model="form.condiciones_suelo">
                <option value="">--SELECCIONE--</option>
                <option value="SECO">SECO</option>
                <option value="MOJADO">MOJADO</option>
                <option value="HUMEDO">HÚMEDO</option>
                <option value="OTRO">OTRO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-clima">Clima</label>
              <select id="lugar-clima" v-model="form.clima">
                <option value="">--SELECCIONE--</option>
                <option value="SECO">SECO</option>
                <option value="CALOR">CALOR</option>
                <option value="LLUVIA">LLUVIA</option>
                <option value="FRIO">FRÍO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-iluminacion">Iluminación</label>
              <select id="lugar-iluminacion" v-model="form.iluminacion">
                <option value="">--SELECCIONE--</option>
                <option value="BUENA">BUENA</option>
                <option value="REGULAR">REGULAR</option>
                <option value="POBRE">POBRE</option>
                <option value="NULA">NULA</option>
              </select>
            </div>
          </div>

          <div class="croquis-panel">
            <h3 class="inspeccion-lugar-minor-heading">Croquis del lugar*</h3>
            <div class="inspeccion-lugar-field">
              <label for="lugar-croquis">URL de la imagen del croquis</label>
              <input
                id="lugar-croquis"
                v-model="form.croquis_imagen_url"
                type="url"
                maxlength="300"
                placeholder="https://"
              />
            </div>
          </div>
        </div>
      </section>

      <section class="inspeccion-lugar-block" aria-labelledby="inspeccion-heading">
        <h2 id="inspeccion-heading" class="inspeccion-lugar-subheading">
          Apartado 4.2 Inspección del lugar
        </h2>

        <div class="inspeccion-lugar-section-content inspeccion-detalles">
          <div class="preguntas-inspeccion">
            <div class="inspeccion-lugar-field">
              <label for="lugar-realizo-inspeccion">¿Realizó la inspección del lugar?*</label>
              <select id="lugar-realizo-inspeccion" v-model="form.realizo_inspeccion">
                <option value="">--SELECCIONE--</option>
                <option :value="true">SÍ</option>
                <option :value="false">NO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-encontro-objeto">
                Al realizar la inspección, ¿encontró algún objeto relacionado con los hechos?*
              </label>
              <select id="lugar-encontro-objeto" v-model="form.encontro_objeto">
                <option value="">--SELECCIONE--</option>
                <option :value="true">SÍ</option>
                <option :value="false">NO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-preservo">¿Preservó el lugar de la intervención?*</label>
              <select id="lugar-preservo" v-model="form.preservo_lugar">
                <option value="">--SELECCIONE--</option>
                <option :value="true">SÍ</option>
                <option :value="false">NO</option>
              </select>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-priorizacion">
                ¿Llevó a cabo la priorización en el lugar de la intervención?*
              </label>
              <select id="lugar-priorizacion" v-model="form.realizo_priorizacion">
                <option value="">--SELECCIONE--</option>
                <option :value="true">SÍ</option>
                <option :value="false">NO</option>
              </select>
            </div>
          </div>

          <fieldset class="riesgo-fieldset">
            <legend>Tipo de riesgo presentado</legend>
            <div class="riesgo-options">
              <label>
                <input v-model="form.tipo_riesgo" type="radio" value="sociales" />
                <span>Sociales</span>
              </label>
              <label>
                <input v-model="form.tipo_riesgo" type="radio" value="naturales" />
                <span>Naturales</span>
              </label>
              <label>
                <input v-model="form.tipo_riesgo" type="radio" value="" />
                <span>Sin riesgo especificado</span>
              </label>
            </div>
            <div class="inspeccion-lugar-field">
              <label for="lugar-especifique-riesgo">Especifique el riesgo</label>
              <textarea
                id="lugar-especifique-riesgo"
                v-model="form.especifique_riesgo"
                rows="3"
              ></textarea>
            </div>
          </fieldset>
        </div>
      </section>

      <div class="inspeccion-lugar-actions">
        <button
          type="button"
          class="inspeccion-lugar-cancel"
          :disabled="guardando"
          @click="emit('cancelar')"
        >
          Cancelar
        </button>
        <button type="submit" class="inspeccion-lugar-save" :disabled="guardando">
          {{ guardando ? "GUARDANDO..." : "GUARDAR SECCIÓN" }}
        </button>
        <button
          type="button"
          class="inspeccion-lugar-next"
          aria-label="Guardar y continuar a la siguiente sección"
          :disabled="guardando"
          @click="guardarYContinuar"
        >
          <span aria-hidden="true">➜</span>
        </button>
      </div>
    </form>

    <Teleport to="body">
      <div v-if="mapaAbierto" class="map-modal-backdrop" @click.self="cerrarMapa">
        <section class="map-modal" role="dialog" aria-modal="true" aria-labelledby="map-modal-title">
          <header class="map-modal-header">
            <div><p class="map-modal-eyebrow">UBICACIÓN GEOGRÁFICA · TAMAULIPAS</p><h2 id="map-modal-title">Selecciona el punto del informe</h2></div>
            <button type="button" class="map-modal-close" aria-label="Cerrar mapa" @click="cerrarMapa">×</button>
          </header>
          <form class="map-search" @submit.prevent="buscarDireccion">
            <label class="sr-only" for="map-address-search">Buscar dirección dentro de Tamaulipas</label>
            <input id="map-address-search" v-model="consultaMapa" type="search" placeholder="Buscar dirección, colonia o municipio…" />
            <button type="submit" :disabled="buscando || !consultaMapa.trim()">{{ buscando ? 'Buscando…' : 'Buscar' }}</button>
          </form>
          <p class="map-message" :class="{ 'map-message-error': errorMapa }" role="status">{{ errorMapa || 'Haz clic en el mapa para seleccionar una ubicación. El punto debe estar dentro de Tamaulipas.' }}</p>
          <div ref="mapElement" class="map-canvas" aria-label="Mapa interactivo de Tamaulipas"></div>
          <footer class="map-modal-footer"><span>© OpenStreetMap contributors</span><div><button type="button" class="map-cancel" @click="cerrarMapa">Cancelar</button><button type="button" class="map-apply" :disabled="!puntoSeleccionado || buscando" @click="aplicarPunto">Usar esta ubicación</button></div></footer>
        </section>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar", "siguiente"]);

const form = ref({
  fecha_inspeccion: "",
  hora_inspeccion: "",
  tipo_lugar: "",
  tipo_suelo: "",
  condiciones_suelo: "",
  clima: "",
  iluminacion: "",
  municipio: "",
  localidad: "",
  colonia: "",
  calle: "",
  entre_calle: "",
  y_calle: "",
  brecha: "",
  kilometro: "",
  no_exterior: "",
  manzana: "",
  lote: "",
  latitud: "0",
  longitud: "0",
  referencias: "",
  realizo_inspeccion: "",
  encontro_objeto: "",
  preservo_lugar: "",
  realizo_priorizacion: "",
  tipo_riesgo: "",
  especifique_riesgo: "",
  croquis_imagen_url: "",
});

const modoUbicacion = ref("punteo");
const guardando = ref(false);
const mapaAbierto = ref(false);
const buscando = ref(false);
const consultaMapa = ref("");
const errorMapa = ref("");
const mapElement = ref(null);
const puntoSeleccionado = ref(null);
let mapa = null;
let marcador = null;
let ultimaPeticionGeo = 0;

// Bounding box de Tamaulipas (sur, oeste, norte, este). El mapa limita el
// desplazamiento a esta extensión y toda selección se valida antes de geocodificar.
const TAMAULIPAS_BOUNDS = L.latLngBounds(
  L.latLng(22.20, -100.00),
  L.latLng(27.70, -97.10),
);
const TAMAULIPAS_CENTER = [24.3, -98.7];

const mapaHref = computed(() => {
  const latitud = Number(form.value.latitud);
  const longitud = Number(form.value.longitud);
  if (
    !form.value.latitud ||
    !form.value.longitud ||
    !Number.isFinite(latitud) ||
    !Number.isFinite(longitud) ||
    (latitud === 0 && longitud === 0)
  ) {
    return "";
  }
  return `https://www.openstreetmap.org/?mlat=${encodeURIComponent(latitud)}&mlon=${encodeURIComponent(longitud)}#map=17/${encodeURIComponent(latitud)}/${encodeURIComponent(longitud)}`;
});

function mapear(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    fecha_inspeccion: data.fecha_inspeccion ?? data.FECHA_INSPECCION ?? "",
    hora_inspeccion: data.hora_inspeccion ?? data.HORA_INSPECCION ?? "",
    tipo_lugar: data.tipo_lugar ?? data.TIPO_LUGAR ?? "",
    tipo_suelo: data.tipo_suelo ?? data.TIPO_SUELO ?? "",
    condiciones_suelo: data.condiciones_suelo ?? data.CONDICIONES_SUELO ?? "",
    clima: data.clima ?? data.CLIMA ?? "",
    iluminacion: data.iluminacion ?? data.ILUMINACION ?? "",
    municipio: data.municipio ?? data.MUNICIPIO ?? "",
    localidad: data.localidad ?? data.LOCALIDAD ?? "",
    colonia: data.colonia ?? data.COLONIA ?? "",
    calle: data.calle ?? data.CALLE ?? "",
    entre_calle: data.entre_calle ?? data.ENTRE_CALLE ?? "",
    y_calle: data.y_calle ?? data.Y_CALLE ?? "",
    brecha: data.brecha ?? data.BRECHA ?? "",
    kilometro: data.kilometro ?? data.KILOMETRO ?? "",
    no_exterior: data.no_exterior ?? data.NO_EXTERIOR ?? "",
    manzana: data.manzana ?? data.MANZANA ?? "",
    lote: data.lote ?? data.LOTE ?? "",
    latitud: data.latitud ?? data.LATITUD ?? "0",
    longitud: data.longitud ?? data.LONGITUD ?? "0",
    referencias: data.referencias ?? data.REFERENCIAS ?? "",
    realizo_inspeccion: data.realizo_inspeccion ?? data.REALIZO_INSPECCION ?? "",
    encontro_objeto: data.encontro_objeto ?? data.ENCONTRO_OBJETO ?? "",
    preservo_lugar: data.preservo_lugar ?? data.PRESERVO_LUGAR ?? "",
    realizo_priorizacion: data.realizo_priorizacion ?? data.REALIZO_PRIORIZACION ?? "",
    tipo_riesgo: data.tipo_riesgo ?? data.TIPO_RIESGO ?? "",
    especifique_riesgo: data.especifique_riesgo ?? data.ESPECIFIQUE_RIESGO ?? "",
    croquis_imagen_url: data.croquis_imagen_url ?? data.CROQUIS_IMAGEN_URL ?? "",
  };
}

function puntoDentroDeTamaulipas(lat, lon) {
  return Number.isFinite(lat) && Number.isFinite(lon) && TAMAULIPAS_BOUNDS.contains(L.latLng(lat, lon));
}

async function abrirMapa() {
  errorMapa.value = "";
  puntoSeleccionado.value = null;
  mapaAbierto.value = true;
  await nextTick();
  if (!mapElement.value || mapa) return;
  mapa = L.map(mapElement.value, {
    center: TAMAULIPAS_CENTER,
    zoom: 6,
    minZoom: 6,
    maxZoom: 19,
    maxBounds: TAMAULIPAS_BOUNDS,
    maxBoundsViscosity: 1,
    zoomControl: true,
  });
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(mapa);
  mapa.fitBounds(TAMAULIPAS_BOUNDS);
  mapa.on("click", (event) => seleccionarCoordenadas(event.latlng.lat, event.latlng.lng));

  const lat = Number(form.value.latitud);
  const lon = Number(form.value.longitud);
  if (puntoDentroDeTamaulipas(lat, lon) && (lat !== 0 || lon !== 0)) {
    puntoSeleccionado.value = { lat, lon, address: null };
    marcador = L.marker([lat, lon]).addTo(mapa);
    mapa.setView([lat, lon], 15);
  }
  window.setTimeout(() => mapa?.invalidateSize(), 100);
}

function cerrarMapa() {
  mapaAbierto.value = false;
  mapa?.remove();
  mapa = null;
  marcador = null;
}

function colocarMarcador(lat, lon) {
  if (!mapa) return;
  if (marcador) marcador.setLatLng([lat, lon]);
  else marcador = L.marker([lat, lon]).addTo(mapa);
  mapa.panTo([lat, lon]);
}

async function esperarLimiteGeocodificacion() {
  // Nominatim público permite como máximo una solicitud por segundo.
  const espera = Math.max(0, 1100 - (Date.now() - ultimaPeticionGeo));
  if (espera) await new Promise((resolve) => window.setTimeout(resolve, espera));
  ultimaPeticionGeo = Date.now();
}

async function reverseGeocodificar(lat, lon) {
  await esperarLimiteGeocodificacion();
  const url = new URL("https://nominatim.openstreetmap.org/reverse");
  url.search = new URLSearchParams({ format: "jsonv2", lat: String(lat), lon: String(lon), addressdetails: "1", zoom: "18", "accept-language": "es" }).toString();
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error("No fue posible consultar la dirección del punto.");
  const data = await response.json();
  if (!esResultadoDeTamaulipas(data)) throw new Error("El punto no pertenece a Tamaulipas. Selecciona una ubicación dentro del estado.");
  return data;
}

function esResultadoDeTamaulipas(data) {
  const estado = data?.address?.state || data?.address?.region || "";
  return /tamaulipas/i.test(estado);
}

async function seleccionarCoordenadas(lat, lon) {
  if (!puntoDentroDeTamaulipas(lat, lon)) {
    errorMapa.value = "La ubicación seleccionada está fuera de Tamaulipas.";
    return;
  }
  errorMapa.value = "";
  puntoSeleccionado.value = { lat, lon, address: null };
  colocarMarcador(lat, lon);
  buscando.value = true;
  try {
    puntoSeleccionado.value.address = await reverseGeocodificar(lat, lon);
  } catch (error) {
    puntoSeleccionado.value = null;
    errorMapa.value = error.message || "No se pudo obtener la dirección. Intenta seleccionar el punto nuevamente.";
  } finally {
    buscando.value = false;
  }
}

async function buscarDireccion() {
  if (!consultaMapa.value.trim()) return;
  errorMapa.value = "";
  buscando.value = true;
  try {
    await esperarLimiteGeocodificacion();
    const url = new URL("https://nominatim.openstreetmap.org/search");
    url.search = new URLSearchParams({ q: `${consultaMapa.value}, Tamaulipas, México`, format: "jsonv2", addressdetails: "1", limit: "5", countrycodes: "mx", viewbox: "-100,27.7,-97.1,22.2", bounded: "1", "accept-language": "es" }).toString();
    const response = await fetch(url, { headers: { Accept: "application/json" } });
    if (!response.ok) throw new Error("No fue posible buscar esa dirección.");
    const resultados = await response.json();
    const resultado = resultados.find((item) => puntoDentroDeTamaulipas(Number(item.lat), Number(item.lon)) && esResultadoDeTamaulipas(item));
    if (!resultado) throw new Error("No encontramos esa dirección dentro de Tamaulipas. Prueba con otro término.");
    const lat = Number(resultado.lat);
    const lon = Number(resultado.lon);
    puntoSeleccionado.value = { lat, lon, address: resultado };
    colocarMarcador(lat, lon);
    mapa?.setView([lat, lon], Math.max(mapa.getZoom(), 16));
  } catch (error) {
    errorMapa.value = error.message || "No fue posible completar la búsqueda.";
  } finally {
    buscando.value = false;
  }
}

function aplicarPunto() {
  const punto = puntoSeleccionado.value;
  if (!punto || !puntoDentroDeTamaulipas(punto.lat, punto.lon)) return;
  const address = punto.address?.address || {};
  const calle = address.road || address.pedestrian || address.residential || address.highway || address.path;
  const localidad = address.city || address.town || address.village || address.municipality || address.city_district;
  const colonia = address.suburb || address.neighbourhood || address.quarter || address.hamlet || address.locality;
  const valores = {
    latitud: punto.lat.toFixed(7),
    longitud: punto.lon.toFixed(7),
    calle,
    municipio: address.municipality || address.county || address.city_district || address.city || address.town,
    localidad,
    colonia,
    entre_calle: address.between || address.crossing,
    y_calle: address.crossing,
    brecha: address.track || address.path,
    no_exterior: address.house_number,
  };
  for (const [campo, valor] of Object.entries(valores)) {
    if (valor !== undefined && valor !== null && valor !== "") form.value[campo] = String(valor);
  }
  cerrarMapa();
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/inspeccion_lugar`);
  mapear(data);
}

async function guardar() {
  guardando.value = true;
  try {
    await api.put(`/iph/${props.iphId}/inspeccion_lugar`, form.value);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function guardarYContinuar() {
  await guardar();
  emit("siguiente");
}

onMounted(cargar);
onBeforeUnmount(cerrarMapa);
</script>

<style scoped>
.inspeccion-lugar-form {
  width: 100%;
  color: #303030;
  font-family: Arial, sans-serif;
}

.inspeccion-lugar-form form {
  display: grid;
  gap: 0.85rem;
}

.inspeccion-lugar-block {
  border: 1px solid #d9d9d9;
  background: #fff;
}

.inspeccion-lugar-subheading {
  margin: 0;
  padding: 0.55rem 0.7rem;
  border-bottom: 1px solid #dedede;
  background: #f2f2f2;
  color: #454545;
  font-size: 0.82rem;
  font-weight: 700;
}

.inspeccion-lugar-section-content {
  display: grid;
  gap: 0.75rem;
  padding: 0.75rem;
}

.ubicacion-modos,
.riesgo-options {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  margin: 0;
  padding: 0.1rem 0;
  border: 0;
}

.ubicacion-modos label,
.riesgo-options label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #333;
  font-size: 0.72rem;
  font-weight: 700;
}

.ubicacion-modos input,
.riesgo-options input {
  accent-color: #555;
}

.map-picker-trigger { display: inline-flex !important; visibility: visible; flex: 0 0 auto; min-height: 2rem; align-items: center; gap: .4rem; padding: .3rem .7rem; border: 1px solid #555; border-radius: 4px; background: #555; color: #fff; font-size: .68rem; font-weight: 700; white-space: nowrap; }
.map-picker-trigger svg { display: block; width: 15px; height: 15px; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.8; }
.map-picker-trigger:hover { background: #3f3f3f; }
.map-modal-backdrop { position: fixed; z-index: 10000; inset: 0; display: grid; place-items: center; padding: 1rem; background: #101a1dcc; }
.map-modal { display: grid; width: min(900px, 100%); max-height: min(760px, 94vh); grid-template-rows: auto auto auto minmax(260px, 1fr) auto; overflow: hidden; border-radius: 12px; background: #fff; box-shadow: 0 24px 70px #0005; color: #24342e; font-family: Arial, sans-serif; }
.map-modal-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 1rem 1.2rem .65rem; }
.map-modal-eyebrow { margin: 0 0 .35rem; color: #666; font-size: .6rem; font-weight: 700; letter-spacing: .12em; }
.map-modal-header h2 { margin: 0; font-size: 1rem; }
.map-modal-close { width: 2rem; height: 2rem; border: 1px solid #dedede; border-radius: 7px; background: white; color: #454545; font-size: 1.35rem; }
.map-search { display: flex; gap: .5rem; padding: .35rem 1.2rem; }
.map-search input { flex: 1; min-width: 0; padding: .65rem .75rem; border: 1px solid #d1d1d1; border-radius: 6px; font-size: .8rem; }
.map-search button,.map-apply { padding: .6rem 1rem; border: 1px solid #555; border-radius: 6px; background: #555; color: #fff; font-size: .72rem; font-weight: 700; }
.map-search button:disabled,.map-apply:disabled { cursor: not-allowed; opacity: .5; }
.map-message { min-height: 1.5rem; margin: .15rem 1.2rem .5rem; color: #666; font-size: .68rem; }.map-message-error { color: #a03737; }
.map-canvas { min-height: 280px; width: 100%; background: #e7e7e7; }
.map-modal-footer { display: flex; align-items: center; justify-content: space-between; gap: .75rem; padding: .8rem 1.2rem; color: #666; font-size: .62rem; }.map-modal-footer > div { display: flex; gap: .5rem; }.map-cancel { padding: .55rem .85rem; border: 1px solid #d8d8d8; border-radius: 6px; background: #fff; color: #454545; font-size: .7rem; }

.ubicacion-coordenadas {
  padding: 0.65rem;
  border: 1px solid #e0e0e0;
  background: #fafafa;
}

.ubicacion-ayuda {
  margin: 0 0 0.6rem;
  color: #555;
  font-size: 0.67rem;
}

.inspeccion-lugar-grid {
  display: grid;
  min-width: 0;
  gap: 0.65rem 1rem;
}

.coordenadas-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr)) minmax(170px, 0.65fr);
  align-items: end;
}

.datos-geograficos-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.datos-lugar-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.inspeccion-lugar-field {
  display: grid;
  min-width: 0;
  gap: 0.25rem;
}

.inspeccion-lugar-field label {
  color: #333;
  font-size: 0.68rem;
}

.inspeccion-lugar-field input,
.inspeccion-lugar-field select,
.inspeccion-lugar-field textarea {
  width: 100%;
  min-height: 1.9rem;
  padding: 0.3rem 0.5rem;
  border: 1px solid #cfcfcf;
  border-radius: 3px;
  background: #fff;
  color: #343434;
  font-size: 0.75rem;
}

.inspeccion-lugar-field textarea {
  min-height: 4rem;
  resize: vertical;
}

.field-span-2 {
  grid-column: span 2;
}

.coordenadas-accion {
  display: flex;
  align-items: end;
  min-height: 1.9rem;
}

.inspeccion-lugar-map-link {
  display: inline-flex;
  min-height: 1.9rem;
  align-items: center;
  justify-content: center;
  padding: 0.35rem 0.7rem;
  border: 1px solid #555;
  border-radius: 3px;
  background: #555;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  text-decoration: none;
}

.inspeccion-lugar-map-hint {
  padding-bottom: 0.35rem;
  color: #666;
  font-size: 0.62rem;
}

.inspeccion-lugar-minor-heading {
  margin: 0;
  padding: 0.42rem 0.6rem;
  border: 1px solid #dedede;
  background: #f6f6f6;
  color: #303030;
  font-size: 0.73rem;
  font-weight: 700;
}

.referencias-field {
  margin-top: 0.1rem;
}

.croquis-panel {
  display: grid;
  gap: 0.6rem;
  padding-top: 0.15rem;
}

.inspeccion-detalles {
  grid-template-columns: minmax(0, 1fr) minmax(250px, 0.8fr);
  align-items: start;
  gap: 1rem;
}

.preguntas-inspeccion {
  display: grid;
  gap: 0.65rem;
}

.preguntas-inspeccion .inspeccion-lugar-field {
  grid-template-columns: minmax(0, 1fr) minmax(120px, 0.45fr);
  align-items: center;
  gap: 0.6rem;
}

.riesgo-fieldset {
  display: grid;
  gap: 0.7rem;
  margin: 0;
  padding: 0.65rem;
  border: 1px solid #dedede;
}

.riesgo-fieldset legend {
  padding: 0 0.25rem;
  color: #333;
  font-size: 0.68rem;
  font-weight: 700;
}

.inspeccion-lugar-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 5vw, 4rem);
  padding: 0.4rem 0 0.2rem;
}

.inspeccion-lugar-actions button {
  min-height: 2rem;
  padding: 0.4rem 0.8rem;
  border-radius: 3px;
  font-size: 0.68rem;
  font-weight: 700;
}

.inspeccion-lugar-cancel {
  border: 1px solid #d0d0d0;
  background: #fff;
  color: #575756;
}

.inspeccion-lugar-save {
  border: 1px solid #575756;
  background: #575756;
  color: #fff;
}

.inspeccion-lugar-save:hover:not(:disabled) {
  background: #434342;
}

.inspeccion-lugar-next {
  display: grid;
  width: 2rem;
  height: 2rem;
  place-items: center;
  border: 0;
  border-radius: 50% !important;
  background: #666;
  color: #fff;
  font-size: 1.2rem !important;
}

.inspeccion-lugar-actions button:disabled {
  cursor: wait;
  opacity: 0.65;
}

@media (max-width: 760px) {
  .coordenadas-grid,
  .datos-geograficos-grid,
  .datos-lugar-grid,
  .inspeccion-detalles {
    grid-template-columns: minmax(0, 1fr);
  }

  .field-span-2 {
    grid-column: auto;
  }

  .preguntas-inspeccion .inspeccion-lugar-field {
    grid-template-columns: minmax(0, 1fr);
  }

  .coordenadas-accion {
    min-height: auto;
  }

  .inspeccion-lugar-actions {
    justify-content: space-around;
    gap: 0.5rem;
  }

  .map-modal-backdrop { padding: .5rem; }
  .map-modal { max-height: 96vh; grid-template-rows: auto auto auto minmax(240px, 1fr) auto; }
  .map-modal-header,.map-search { padding-right: .8rem; padding-left: .8rem; }
  .map-message { margin-right: .8rem; margin-left: .8rem; }
  .map-modal-footer { align-items: flex-start; flex-direction: column; padding: .65rem .8rem; }
  .map-modal-footer > div { width: 100%; }
  .map-modal-footer button { flex: 1; }
}
</style>
