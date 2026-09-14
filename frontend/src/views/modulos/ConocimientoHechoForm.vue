<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-2xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Conocimiento de Hecho</h2>

    <form @submit.prevent="guardar" class="space-y-4">
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
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha de conocimiento</label>
          <input v-model="form.fecha_conocimiento" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Hora de conocimiento</label>
          <input v-model="form.hora_conocimiento" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>
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
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);

const form = ref({
  como_se_entero: "",
  numero_911: "",
  fecha_conocimiento: "",
  hora_conocimiento: "",
  fecha_arribo: "",
  hora_arribo: "",
});
const guardando = ref(false);

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/conocimiento_hecho`);
  if (data) {
    form.value = { ...form.value, ...data };
  }
}

async function guardar() {
  guardando.value = true;
  try {
    await api.put(`/iph/${props.iphId}/conocimiento_hecho`, form.value);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
