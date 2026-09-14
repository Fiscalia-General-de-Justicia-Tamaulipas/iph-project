<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-4xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Conocimiento de Hecho</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
        <div class="xl:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">INSTITUCIÓN / UNIDAD QUE INFORMA</label>
          <select v-model="form.id_institucion_informante" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="1">Policía Ministerial</option>
            <option value="2">Fiscalía</option>
            <option value="3">Agencia Ministerial</option>
            <option value="4">Otra institución</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DEL CONOCIMIENTO</label>
          <input v-model="form.fecha_conocimiento" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA DEL CONOCIMIENTO</label>
          <input v-model="form.hora_conocimiento" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CARGO O AUTORIDAD</label>
          <select v-model="form.id_cargo" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="8">Policía Investigador</option>
            <option value="16">Comandante</option>
            <option value="20">Agente de policía</option>
            <option value="21">Fiscal</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESTADO</label>
          <select v-model="form.id_estado" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="28">Tamaulipas</option>
            <option value="1">Aguascalientes</option>
            <option value="29">Veracruz</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MUNICIPIO</label>
          <select v-model="form.id_municipio" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="41">Victoria</option>
            <option value="42">Ciudad Mante</option>
            <option value="43">Matamoros</option>
          </select>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">¿Cómo se enteró del hecho?</label>
        <select v-model="form.como_se_entero" class="w-full border rounded-md px-3 py-2">
          <option value="">Selecciona una opción</option>
          <option value="denuncia">Denuncia</option>
          <option value="flagrancia">Flagrancia</option>
          <option value="localizacion">Localización</option>
          <option value="mandamiento_judicial">Mandamiento judicial</option>
          <option value="llamada_emergencia">Llamada de emergencia</option>
          <option value="descubrimiento">Descubrimiento</option>
          <option value="aportacion">Aportación</option>
        </select>
      </div>

      <div v-if="form.como_se_entero === 'llamada_emergencia'">
        <label class="block text-sm font-medium text-gray-700 mb-1">No. 911</label>
        <input v-model="form.numero_911" class="w-full border rounded-md px-3 py-2" />
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de arribo</label>
          <input v-model="form.fecha_arribo" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Hora de arribo</label>
          <input v-model="form.hora_arribo" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>
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
import { useAuthStore } from "../../store/auth";
import api from "../../store/api";

const auth = useAuthStore();
const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);

const form = ref({
  id_institucion_informante: "",
  fecha_conocimiento: "",
  hora_conocimiento: "00:00",
  id_cargo: "",
  id_estado: "28",
  id_municipio: auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? "41",
  como_se_entero: "",
  numero_911: "",
  fecha_arribo: "",
  hora_arribo: "00:00",
});
const guardando = ref(false);

function mapearRegistro(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    id_institucion_informante: data.id_institucion_informante ?? data.ID_INSTITUCION_INFORMANTE ?? data.id_institucion ?? "",
    fecha_conocimiento: data.fecha_conocimiento ?? data.FECHA_CONOCIMIENTO ?? "",
    hora_conocimiento: data.hora_conocimiento ?? data.HORA_CONOCIMIENTO ?? "00:00",
    id_cargo: data.id_cargo ?? data.ID_CARGO ?? "",
    id_estado: data.id_estado ?? data.ID_ESTADO ?? "28",
    id_municipio: data.id_municipio ?? data.ID_MUNICIPIO ?? auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? "41",
    como_se_entero: data.como_se_entero ?? data.COMO_SE_ENTERO ?? "",
    numero_911: data.numero_911 ?? data.NUMERO_911 ?? "",
    fecha_arribo: data.fecha_arribo ?? data.FECHA_ARRIBO ?? "",
    hora_arribo: data.hora_arribo ?? data.HORA_ARRIBO ?? "00:00",
  };
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/conocimiento_hecho`);
  if (data) {
    mapearRegistro(data);
  }
}

async function guardar() {
  guardando.value = true;
  try {
    const payload = {
      ...form.value,
      id_usuario: auth.usuario?.id_usuario ?? auth.usuario?.id ?? null,
      id_estado: form.value.id_estado || 28,
      id_municipio: form.value.id_municipio || auth.usuario?.id_municipio || auth.usuario?.IdMunicipio || 41,
    };
    await api.put(`/iph/${props.iphId}/conocimiento_hecho`, payload);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
