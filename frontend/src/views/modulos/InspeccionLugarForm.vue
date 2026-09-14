<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-5xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Inspección de Lugar</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">DÍA / MES / AÑO</label>
          <input v-model="form.fecha_inspeccion" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA:MIN</label>
          <input v-model="form.hora_inspeccion" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div class="xl:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE LUGAR</label>
          <select v-model="form.tipo_lugar" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="VIVIENDA">VIVIENDA</option>
            <option value="CALLE">CALLE</option>
            <option value="PREDIO">PREDIO</option>
            <option value="NEGOCIO">NEGOCIO</option>
            <option value="VEHICULO">VEHÍCULO</option>
            <option value="OTRO">OTRO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE SUELO</label>
          <select v-model="form.tipo_suelo" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="ARENOSO">ARENOSO</option>
            <option value="ARCILLOSO">ARCILLOSO</option>
            <option value="PEDREGOSO">PEDREGOSO</option>
            <option value="OTRO">OTRO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CONDICIONES DEL SUELO</label>
          <select v-model="form.condiciones_suelo" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="SECO">SECO</option>
            <option value="MOJADO">MOJADO</option>
            <option value="HUMEDO">HUMEDO</option>
            <option value="OTRO">OTRO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CLIMA</label>
          <select v-model="form.clima" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="SECO">SECO</option>
            <option value="CALOR">CALOR</option>
            <option value="LLUVIA">LLUVIA</option>
            <option value="FRIO">FRIO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ILUMINACIÓN</label>
          <select v-model="form.iluminacion" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="BUENA">BUENA</option>
            <option value="REGULAR">REGULAR</option>
            <option value="POBRE">POBRE</option>
            <option value="NULA">NULA</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MUNICIPIO</label>
          <input v-model="form.municipio" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LOCALIDAD</label>
          <input v-model="form.localidad" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div class="xl:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">COLONIA / FRACCIONAMIENTO</label>
          <input v-model="form.colonia" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div class="xl:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">CALLE</label>
          <input v-model="form.calle" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ENTRE CALLE</label>
          <input v-model="form.entre_calle" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Y CALLE</label>
          <input v-model="form.y_calle" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">BRECHA</label>
          <input v-model="form.brecha" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">KILÓMETRO</label>
          <input v-model="form.kilometro" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">NO. EXTERIOR</label>
          <input v-model="form.no_exterior" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MANZANA</label>
          <input v-model="form.manzana" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LOTE</label>
          <input v-model="form.lote" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LATITUD</label>
          <input v-model="form.latitud" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LONGITUD</label>
          <input v-model="form.longitud" class="w-full border rounded-md px-3 py-2" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">REFERENCIAS</label>
        <textarea v-model="form.referencias" rows="4" class="w-full border rounded-md px-3 py-2"></textarea>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE REALIZÓ LA INSPECCIÓN?</label>
          <select v-model="form.realizo_inspeccion" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE ENCONTRÓ OBJETO?</label>
          <select v-model="form.encontro_objeto" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE PRESERVÓ EL LUGAR?</label>
          <select v-model="form.preservo_lugar" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE REALIZÓ PRIORIZACIÓN?</label>
          <select v-model="form.realizo_priorizacion" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>
      </div>

      <div class="flex gap-3 justify-end">
        <button type="button" class="border border-[#d0d0d0] bg-white px-4 py-2 rounded-md text-[#575756] hover:bg-[#f7f7f7]" @click="$emit('cancelar')">Cancelar</button>
        <button
          type="submit"
          :disabled="guardando"
          class="bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
        >
          {{ guardando ? "Guardando..." : "Guardar" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar"]);

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
});

const guardando = ref(false);

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
  };
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

onMounted(cargar);
</script>
