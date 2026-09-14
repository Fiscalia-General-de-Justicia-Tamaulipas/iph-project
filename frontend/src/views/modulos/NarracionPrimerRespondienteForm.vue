<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-5xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Narración del primer respondiente</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NARRATIVA</label>
        <textarea
          v-model="form.narrativa"
          rows="18"
          class="w-full border rounded-md px-3 py-2 resize-none"
          placeholder="Escriba aquí la narración de los hechos y la actuación del primer respondiente..."
        ></textarea>
      </div>

      <div class="flex justify-end">
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
const emit = defineEmits(["guardado"]);

const guardando = ref(false);
const form = ref({
  narrativa: "",
});

function mapear(data) {
  if (!data) return;
  form.value = {
    narrativa: data.narrativa ?? data.NARRATIVA ?? data.descripcion ?? data.DESCRIPCION ?? "",
  };
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/narracion_primer_respondiente`);
  mapear(data);
}

async function guardar() {
  guardando.value = true;
  try {
    await api.put(`/iph/${props.iphId}/narracion_primer_respondiente`, {
      narrativa: form.value.narrativa,
    });
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
