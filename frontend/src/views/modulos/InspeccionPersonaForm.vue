<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-4xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Inspección de Persona</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">IMPUTADO</label>
        <select v-model="form.imputado_id" class="w-full border rounded-md px-3 py-2">
          <option value="">--SELECCIONE--</option>
          <option v-for="item in imputados" :key="item.id" :value="item.id">
            {{ item.nombres || "Sin nombre" }} {{ item.primer_apellido || "" }} {{ item.segundo_apellido || "" }}
          </option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NARRATIVA DE LA INSPECCIÓN DE LA PERSONA DETENIDA</label>
        <textarea v-model="form.narrativa" rows="6" class="w-full border rounded-md px-3 py-2"></textarea>
      </div>

      <div class="grid md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">CANTIDAD</label>
          <input v-model="form.cantidad_objeto" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE OBJETO</label>
          <input v-model="form.tipo_objeto" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">DESCRIPCIÓN</label>
          <input v-model="form.descripcion_objeto" class="w-full border rounded-md px-3 py-2" />
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE ENCONTRÓ OBJETO?</label>
          <select v-model="form.encontro_objeto" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option :value="true">SI</option>
            <option :value="false">NO</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">¿SE RECOLECTARON PERTENENCIAS?</label>
          <select v-model="form.recolecto_pertenencias" class="w-full border rounded-md px-3 py-2">
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

const imputados = ref([]);
const guardando = ref(false);
const form = ref({
  imputado_id: "",
  narrativa: "",
  cantidad_objeto: "",
  tipo_objeto: "",
  descripcion_objeto: "",
  encontro_objeto: "",
  recolecto_pertenencias: "",
});

function mapear(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    imputado_id: data.imputado_id ?? data.id_imputado ?? data.ID_IMPUTADO ?? data.ID_PERSONA ?? "",
    narrativa: data.narrativa ?? data.NARRATIVA ?? "",
    cantidad_objeto: data.cantidad_objeto ?? data.CANTIDAD_OBJETO ?? "",
    tipo_objeto: data.tipo_objeto ?? data.TIPO_OBJETO ?? "",
    descripcion_objeto: data.descripcion_objeto ?? data.DESCRIPCION_OBJETO ?? "",
    encontro_objeto: data.encontro_objeto ?? data.ENCONTRO_OBJETO ?? "",
    recolecto_pertenencias: data.recolecto_pertenencias ?? data.RECOLECTO_PERTENENCIAS ?? "",
  };
}

async function cargarImputados() {
  const { data } = await api.get(`/iph/${props.iphId}/imputados/lista`);
  imputados.value = data || [];
}

async function cargar() {
  await cargarImputados();
  const { data } = await api.get(`/iph/${props.iphId}/inspeccion_persona`);
  mapear(data);
}

async function guardar() {
  guardando.value = true;
  try {
    const payload = {
      ...form.value,
      imputado_id: form.value.imputado_id || null,
      encontro_objeto: form.value.encontro_objeto === true || form.value.encontro_objeto === 1 || form.value.encontro_objeto === "1" ? 1 : 0,
      recolecto_pertenencias: form.value.recolecto_pertenencias === true || form.value.recolecto_pertenencias === 1 || form.value.recolecto_pertenencias === "1" ? 1 : 0,
    };
    await api.put(`/iph/${props.iphId}/inspeccion_persona`, payload);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
