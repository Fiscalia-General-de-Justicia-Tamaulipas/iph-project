<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-4xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Acciones Realizadas</h2>

    <div class="mb-6 space-y-3">
      <div v-for="accion in lista" :key="accion.id" class="border rounded-md p-3 bg-gray-50">
        <div class="flex justify-between items-start gap-4">
          <div>
            <p class="text-sm font-semibold text-gray-700">{{ accion.orden || 1 }}</p>
            <p class="text-sm text-gray-700 whitespace-pre-line">{{ accion.descripcion }}</p>
            <p class="text-xs text-gray-500 mt-1">
              {{ accion.fecha || "Sin fecha" }} {{ accion.hora ? `- ${accion.hora}` : "" }}
            </p>
          </div>
          <button @click="eliminar(accion.id)" class="text-xs text-red-600 hover:underline">Eliminar</button>
        </div>
      </div>
      <p v-if="lista.length === 0" class="text-sm text-gray-400">Aún no hay acciones realizadas registradas.</p>
    </div>

    <form @submit.prevent="agregar" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NÚMERO DE ORDEN</label>
        <input v-model.number="form.orden" type="number" min="1" class="w-full border rounded-md px-3 py-2" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ACCIONES REALIZADAS</label>
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3 mt-2">
          <label v-for="opcion in opciones" :key="opcion.value" class="flex items-center gap-2 border rounded-md px-3 py-2 text-sm text-gray-700">
            <input v-model="form.opciones" type="checkbox" :value="opcion.value" class="h-4 w-4" />
            {{ opcion.label }}
          </label>
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

      <button
        type="submit"
        :disabled="guardando"
        class="bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
      >
        {{ guardando ? "Guardando..." : "Agregar acción" }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado"]);

const opciones = [
  { value: "AUXILIO", label: "AUXILIO" },
  { value: "INTERVENCIÓN", label: "INTERVENCIÓN" },
  { value: "PRIORIZACIÓN", label: "PRIORIZACIÓN" },
  { value: "ENTREGA / RECEPCIÓN LUGAR HECHOS", label: "ENTREGA / RECEPCIÓN LUGAR HECHOS" },
  { value: "VICTIMA(S)", label: "VICTIMA(S)" },
  { value: "OFENDIDO(S)", label: "OFENDIDO(S)" },
  { value: "TESTIGO(S)", label: "TESTIGO(S)" },
  { value: "DENUNCIANTE(S)", label: "DENUNCIANTE(S)" },
];

const lista = ref([]);
const guardando = ref(false);
const form = ref({
  orden: 1,
  opciones: [],
  descripcion: "",
  fecha: "",
  hora: "",
});

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/acciones_realizadas/lista`);
  lista.value = data || [];
}

function prepararDescripcion() {
  const seleccionados = form.value.opciones?.length ? form.value.opciones.join("; ") : "";
  const descripcionBase = form.value.descripcion?.trim() || "";
  if (!seleccionados && !descripcionBase) {
    return "";
  }
  return [seleccionados, descripcionBase].filter(Boolean).join(" - ");
}

async function agregar() {
  if (!form.value.descripcion.trim() && !form.value.opciones.length) return;
  guardando.value = true;
  try {
    const payload = {
      ...form.value,
      descripcion: prepararDescripcion(),
    };
    await api.post(`/iph/${props.iphId}/acciones_realizadas/lista`, payload);
    form.value = { orden: lista.value.length + 1, opciones: [], descripcion: "", fecha: "", hora: "" };
    await cargar();
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function eliminar(id) {
  await api.delete(`/iph/${props.iphId}/acciones_realizadas/lista/${id}`);
  await cargar();
  emit("guardado");
}

onMounted(cargar);
</script>
