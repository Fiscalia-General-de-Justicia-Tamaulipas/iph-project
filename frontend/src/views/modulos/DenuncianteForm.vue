<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-3xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Denunciante(s)</h2>

    <!-- Lista de denunciantes ya capturados -->
    <div class="divide-y mb-6">
      <div v-for="d in lista" :key="d.id" class="py-3 flex justify-between items-center">
        <div>
          <p class="font-medium">{{ d.primer_apellido }} {{ d.segundo_apellido }} {{ d.nombres }}</p>
          <p class="text-xs text-gray-500">{{ d.telefono || "Sin teléfono" }}</p>
        </div>
        <button @click="eliminar(d.id)" class="text-red-500 text-sm hover:underline">Eliminar</button>
      </div>
      <p v-if="lista.length === 0" class="text-gray-400 text-sm py-2">Aún no hay denunciantes capturados.</p>
    </div>

    <!-- Formulario para agregar uno nuevo -->
    <h3 class="font-medium text-gray-700 mb-2">Agregar denunciante</h3>
    <form @submit.prevent="agregar" class="grid grid-cols-2 gap-4">
      <input v-model="form.primer_apellido" placeholder="Primer apellido" class="border rounded-md px-3 py-2" />
      <input v-model="form.segundo_apellido" placeholder="Segundo apellido" class="border rounded-md px-3 py-2" />
      <input v-model="form.nombres" placeholder="Nombre(s)" class="border rounded-md px-3 py-2 col-span-2" />
      <select v-model="form.sexo" class="border rounded-md px-3 py-2">
        <option value="">Sexo</option>
        <option value="mujer">Mujer</option>
        <option value="hombre">Hombre</option>
      </select>
      <select v-model="form.nacionalidad" class="border rounded-md px-3 py-2">
        <option value="">Nacionalidad</option>
        <option value="mexicana">Mexicana</option>
        <option value="extranjera">Extranjera</option>
      </select>
      <input v-model="form.telefono" placeholder="Teléfono" class="border rounded-md px-3 py-2" />
      <input v-model="form.correo" placeholder="Correo electrónico" class="border rounded-md px-3 py-2" />
      <textarea v-model="form.relato" placeholder="Relato de la denuncia" class="border rounded-md px-3 py-2 col-span-2" rows="3"></textarea>

      <button
        type="submit"
        :disabled="guardando"
        class="col-span-2 bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
      >
        {{ guardando ? "Agregando..." : "Agregar denunciante" }}
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
  primer_apellido: "",
  segundo_apellido: "",
  nombres: "",
  sexo: "",
  nacionalidad: "",
  telefono: "",
  correo: "",
  relato: "",
});

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/denunciantes/lista`);
  lista.value = data;
}

async function agregar() {
  guardando.value = true;
  try {
    await api.post(`/iph/${props.iphId}/denunciantes/lista`, form.value);
    form.value = { primer_apellido: "", segundo_apellido: "", nombres: "", sexo: "", nacionalidad: "", telefono: "", correo: "", relato: "" };
    await cargar();
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function eliminar(id) {
  await api.delete(`/iph/${props.iphId}/denunciantes/lista/${id}`);
  await cargar();
  emit("guardado");
}

onMounted(cargar);
</script>
