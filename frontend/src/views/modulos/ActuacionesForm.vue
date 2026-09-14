<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-4xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Actuaciones</h2>

    <div class="mb-6 space-y-3">
      <div v-for="item in lista" :key="item.id" class="border rounded-md p-3 bg-gray-50">
        <div class="flex justify-between items-start gap-4">
          <div>
            <p class="text-sm font-semibold text-gray-700">{{ item.tipo_actuacion || "Sin tipo" }}</p>
            <p class="text-sm text-gray-700 whitespace-pre-line">{{ item.descripcion || "Sin descripción" }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ item.responsable ? `Responsable: ${item.responsable}` : "Responsable no especificado" }}
              <span v-if="item.fecha || item.hora"> · {{ item.fecha || "Sin fecha" }} {{ item.hora ? `- ${item.hora}` : "" }}</span>
            </p>
          </div>
          <button @click="eliminar(item.id)" class="text-xs text-red-600 hover:underline">Eliminar</button>
        </div>
      </div>
      <p v-if="lista.length === 0" class="text-sm text-gray-400">Aún no hay actuaciones registradas.</p>
    </div>

    <form @submit.prevent="agregar" class="space-y-4">
      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE ACTUACIÓN</label>
          <input v-model="form.tipo_actuacion" class="w-full border rounded-md px-3 py-2" placeholder="Ej.: entrevista, seguimiento, diligencia" required />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">RESPONSABLE</label>
          <input v-model="form.responsable" class="w-full border rounded-md px-3 py-2" placeholder="Nombre del responsable" />
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">DESCRIPCIÓN</label>
        <textarea v-model="form.descripcion" rows="4" class="w-full border rounded-md px-3 py-2" required></textarea>
      </div>

      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA</label>
          <input v-model="form.fecha" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA</label>
          <input v-model="form.hora" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>
      </div>

      <div class="flex gap-3 justify-end">
        <button type="button" class="border border-[#d0d0d0] bg-white px-4 py-2 rounded-md text-[#575756] hover:bg-[#f7f7f7]" @click="$emit('cancelar')">Cancelar</button>
        <button
          type="submit"
          :disabled="guardando"
          class="bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
        >
          {{ guardando ? "Guardando..." : "Agregar actuación" }}
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

const lista = ref([]);
const guardando = ref(false);
const form = ref({
  tipo_actuacion: "",
  descripcion: "",
  responsable: "",
  fecha: "",
  hora: "",
});

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/actuaciones/lista`);
  lista.value = data || [];
}

async function agregar() {
  guardando.value = true;
  try {
    await api.post(`/iph/${props.iphId}/actuaciones/lista`, {
      ...form.value,
    });
    form.value = { tipo_actuacion: "", descripcion: "", responsable: "", fecha: "", hora: "" };
    await cargar();
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function eliminar(id) {
  await api.delete(`/iph/${props.iphId}/actuaciones/lista/${id}`);
  await cargar();
  emit("guardado");
}

onMounted(cargar);
</script>
