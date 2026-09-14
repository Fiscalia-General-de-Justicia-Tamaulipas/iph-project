<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-6xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Inspección de Vehículo</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="xl:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">NÚMERO DE ACCIDENTE VIAL</label>
          <input v-model="form.numero_accidente" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">DELITO</label>
          <input v-model="form.delito" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SERIE</label>
          <input v-model="form.no_serie" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PLACA</label>
          <input v-model="form.placa_matricula" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESTADO DE LA PLACA</label>
          <select v-model="form.estado_placa" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="NACIONAL">NACIONAL</option>
            <option value="ESTATAL">ESTATAL</option>
            <option value="EXTRANJERA">EXTRANJERA</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">NÚMERO DE MOTOR</label>
          <input v-model="form.numero_motor" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MARCA</label>
          <input v-model="form.marca" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SUBMARCA</label>
          <input v-model="form.submarca" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MODELO</label>
          <input v-model="form.modelo" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">COLOR</label>
          <input v-model="form.color" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PROCEDENCIA</label>
          <select v-model="form.procedencia" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="NACIONAL">NACIONAL</option>
            <option value="EXTRANJERO">EXTRANJERO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PLACA EXTRANJERA</label>
          <input v-model="form.placa_extranjera" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE VEHÍCULO</label>
          <input v-model="form.tipo_vehiculo" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PUESTO A DISPOSICIÓN</label>
          <input v-model="form.disposicion" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ASEGURADORA</label>
          <input v-model="form.aseguradora" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE USO</label>
          <input v-model="form.tipo_uso" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">PROPIETARIO</label>
          <input v-model="form.propietario" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESTADO DEL VEHÍCULO</label>
          <input v-model="form.estado_vehiculo" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ASEGURADO POR</label>
          <input v-model="form.asegurado_por" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">REGISTRO VEHICULAR</label>
          <input v-model="form.registro_vehicular" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DE ROBO</label>
          <input v-model="form.fecha_robo" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA DE ROBO</label>
          <input v-model="form.hora_robo" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DE RECUPERADO</label>
          <input v-model="form.fecha_recuperado" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA DE RECUPERADO</label>
          <input v-model="form.hora_recuperado" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">DEPOSITADO EN</label>
          <input v-model="form.depositado_en" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DE DEPOSITO</label>
          <input v-model="form.fecha_deposito" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA DE DEPOSITO</label>
          <input v-model="form.hora_deposito" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESTADO DE RECUPERACIÓN</label>
          <input v-model="form.estado_recuperacion" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MUNICIPIO DE RECUPERACIÓN</label>
          <input v-model="form.municipio_recuperacion" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LOCALIDAD DE RECUPERACIÓN</label>
          <input v-model="form.localidad_recuperacion" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESTADO DE LA INSPECCIÓN</label>
          <select v-model="form.encontro_objetos" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">OBSERVACIONES</label>
        <textarea v-model="form.observaciones" rows="4" class="w-full border rounded-md px-3 py-2"></textarea>
      </div>

      <button
        type="submit"
        :disabled="guardando"
        class="bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
      >
        {{ guardando ? "Guardando..." : "Guardar" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);

const guardando = ref(false);
const form = ref({
  numero_accidente: "",
  delito: "",
  no_serie: "",
  placa_matricula: "",
  estado_placa: "",
  numero_motor: "",
  marca: "",
  submarca: "",
  modelo: "",
  color: "",
  procedencia: "",
  placa_extranjera: "",
  tipo_vehiculo: "",
  disposicion: "",
  aseguradora: "",
  tipo_uso: "",
  propietario: "",
  estado_vehiculo: "",
  asegurado_por: "",
  registro_vehicular: "",
  fecha_robo: "",
  hora_robo: "",
  fecha_recuperado: "",
  hora_recuperado: "",
  depositado_en: "",
  fecha_deposito: "",
  hora_deposito: "",
  estado_recuperacion: "",
  municipio_recuperacion: "",
  localidad_recuperacion: "",
  encontro_objetos: "",
  observaciones: "",
});

function mapear(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    numero_accidente: data.numero_accidente ?? data.NUMERO_ACCIDENTE ?? "",
    delito: data.delito ?? data.DELITO ?? "",
    no_serie: data.no_serie ?? data.NO_SERIE ?? "",
    placa_matricula: data.placa_matricula ?? data.PLACA_MATRICULA ?? "",
    estado_placa: data.estado_placa ?? data.ESTADO_PLACA ?? "",
    numero_motor: data.numero_motor ?? data.NUMERO_MOTOR ?? "",
    marca: data.marca ?? data.MARCA ?? "",
    submarca: data.submarca ?? data.SUBMARCA ?? "",
    modelo: data.modelo ?? data.MODELO ?? "",
    color: data.color ?? data.COLOR ?? "",
    procedencia: data.procedencia ?? data.PROCEDENCIA ?? "",
    placa_extranjera: data.placa_extranjera ?? data.PLACA_EXTRANJERA ?? "",
    tipo_vehiculo: data.tipo_vehiculo ?? data.TIPO_VEHICULO ?? data.tipo ?? "",
    disposicion: data.disposicion ?? data.DISPOSICION ?? "",
    aseguradora: data.aseguradora ?? data.ASEGURADORA ?? "",
    tipo_uso: data.tipo_uso ?? data.TIPO_USO ?? "",
    propietario: data.propietario ?? data.PROPIETARIO ?? "",
    estado_vehiculo: data.estado_vehiculo ?? data.ESTADO_VEHICULO ?? "",
    asegurado_por: data.asegurado_por ?? data.ASEGURADO_POR ?? "",
    registro_vehicular: data.registro_vehicular ?? data.REGISTRO_VEHICULAR ?? "",
    fecha_robo: data.fecha_robo ?? data.FECHA_ROBO ?? "",
    hora_robo: data.hora_robo ?? data.HORA_ROBO ?? "",
    fecha_recuperado: data.fecha_recuperado ?? data.FECHA_RECUPERADO ?? "",
    hora_recuperado: data.hora_recuperado ?? data.HORA_RECUPERADO ?? "",
    depositado_en: data.depositado_en ?? data.DEPOSITADO_EN ?? "",
    fecha_deposito: data.fecha_deposito ?? data.FECHA_DEPOSITO ?? "",
    hora_deposito: data.hora_deposito ?? data.HORA_DEPOSITO ?? "",
    estado_recuperacion: data.estado_recuperacion ?? data.ESTADO_RECUPERACION ?? "",
    municipio_recuperacion: data.municipio_recuperacion ?? data.MUNICIPIO_RECUPERACION ?? "",
    localidad_recuperacion: data.localidad_recuperacion ?? data.LOCALIDAD_RECUPERACION ?? "",
    encontro_objetos: data.encontro_objetos ?? data.ENCONTRO_OBJETOS ?? "",
    observaciones: data.observaciones ?? data.OBSERVACIONES ?? "",
  };
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/inspeccion_vehiculo`);
  mapear(data);
}

async function guardar() {
  guardando.value = true;
  try {
    const payload = { ...form.value };
    await api.put(`/iph/${props.iphId}/inspeccion_vehiculo`, payload);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
