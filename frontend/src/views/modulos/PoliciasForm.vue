<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-4xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Policías actuantes</h2>

    <div class="divide-y mb-6">
      <div v-for="p in lista" :key="p.id" class="py-3 flex justify-between items-center">
        <div>
          <p class="font-medium">{{ p.nombres || p.nombre || "Sin nombre" }} {{ p.primer_apellido || p.paterno || "" }} {{ p.segundo_apellido || p.materno || "" }}</p>
          <p class="text-xs text-gray-500">{{ p.grado_cargo || p.cargo || "Sin grado" }} · {{ p.institucion || "Sin institución" }}</p>
        </div>
        <button @click="eliminar(p.id)" class="text-red-500 text-sm hover:underline">Eliminar</button>
      </div>
      <p v-if="lista.length === 0" class="text-gray-400 text-sm py-2">Aún no hay policías capturados.</p>
    </div>

    <h3 class="font-medium text-gray-700 mb-3">Agregar policía</h3>
    <form @submit.prevent="agregar" class="grid md:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NOMBRE</label>
        <input v-model="form.nombres" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">PATERNO</label>
        <input v-model="form.primer_apellido" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">MATERNO</label>
        <input v-model="form.segundo_apellido" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">GRADO</label>
        <select v-model="form.id_cargo" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="8">Policía Investigador</option>
          <option value="16">Comandante</option>
          <option value="20">Agente de policía</option>
          <option value="21">Fiscal</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">INSTITUCIÓN</label>
        <select v-model="form.institucion" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="guardia_nacional">Guardia Nacional</option>
          <option value="policia_federal_ministerial">Policía Federal Ministerial</option>
          <option value="policia_ministerial">Policía Ministerial</option>
          <option value="policia_mando_unico">Policía de mando único</option>
          <option value="policia_estatal">Policía Estatal</option>
          <option value="policia_municipal">Policía Municipal</option>
          <option value="otra">Otra</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">INSTITUCIÓN OTRO</label>
        <input v-model="form.institucion_otra" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">¿ES POLICÍA RESPONSABLE?</label>
        <select v-model="form.pol_responsable" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="1">SI</option>
          <option value="0">NO</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">¿LOS HECHOS FUERON CIERTOS?</label>
        <select v-model="form.hechos_ciertos" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="1">SI</option>
          <option value="0">NO</option>
        </select>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">UNIDAD DE ARRIBO</label>
        <input v-model="form.unidad_arribo" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">¿ES PRIMER RESPONDIENTE?</label>
        <select v-model="form.es_primer_respondiente" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="1">SI</option>
          <option value="0">NO</option>
        </select>
      </div>

      <button
        type="submit"
        :disabled="guardando"
        class="md:col-span-2 bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
      >
        {{ guardando ? "Agregando..." : "Agregar policía" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);

const lista = ref([]);
const guardando = ref(false);
const form = ref({
  nombres: "",
  primer_apellido: "",
  segundo_apellido: "",
  id_cargo: "",
  institucion: "",
  institucion_otra: "",
  pol_responsable: "",
  hechos_ciertos: "",
  unidad_arribo: "",
  es_primer_respondiente: "",
});

function limpiar() {
  form.value = {
    nombres: "",
    primer_apellido: "",
    segundo_apellido: "",
    id_cargo: "",
    institucion: "",
    institucion_otra: "",
    pol_responsable: "",
    hechos_ciertos: "",
    unidad_arribo: "",
    es_primer_respondiente: "",
  };
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
  lista.value = data || [];
}

async function agregar() {
  guardando.value = true;
  try {
    const payload = {
      ...form.value,
      pol_responsable: form.value.pol_responsable === "1" || form.value.pol_responsable === true ? 1 : 0,
      hechos_ciertos: form.value.hechos_ciertos === "1" || form.value.hechos_ciertos === true ? 1 : 0,
      es_primer_respondiente: form.value.es_primer_respondiente === "1" || form.value.es_primer_respondiente === true ? 1 : 0,
      id_tipo_actor: 5,
    };
    await api.post(`/iph/${props.iphId}/policias/lista`, payload);
    limpiar();
    await cargar();
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function eliminar(id) {
  await api.delete(`/iph/${props.iphId}/policias/lista/${id}`);
  await cargar();
  emit("guardado");
}

onMounted(cargar);
</script>
