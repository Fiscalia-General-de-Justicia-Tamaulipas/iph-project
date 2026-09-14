<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-5xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">Acta de Noticia del Hecho</h2>

    <form @submit.prevent="guardar" class="space-y-6">
      <div class="grid md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE EVENTO</label>
          <select v-model="form.tipo_evento" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="HOMICIDIO">Homicidio</option>
            <option value="LESIONES">Lesiones</option>
            <option value="ROBO">Robo</option>
            <option value="SECUESTRO">Secuestro</option>
            <option value="OTRO">Otro</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">SE RECIBIÓ NOTICIA MEDIANTE</label>
          <select v-model="form.medio_noticia" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="1">Denuncia anónima / Reserva de identidad</option>
            <option value="2">Denuncia con datos del denunciante</option>
            <option value="3">Flagrancia</option>
            <option value="4">Localización, descubrimiento o aportación de indicios</option>
            <option value="5">Otros</option>
          </select>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">ESPECIFIQUE</label>
          <input v-model="form.especifica_noticia" class="w-full border rounded-md px-3 py-2" maxlength="200" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE DELITO QUE FUE REPORTADO AL PRIMER RESPONDIENTE</label>
          <select v-model="form.tipo_delito" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="HOMICIDIO">Homicidio</option>
            <option value="ROBO">Robo</option>
            <option value="LESIONES">Lesiones</option>
            <option value="VIOLENCIA_FAMILIAR">Violencia familiar</option>
            <option value="FUERZA">Fuerza</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DEL ARRIBO</label>
          <input v-model="form.fecha_arribo" type="date" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">HORA DEL ARRIBO</label>
          <input v-model="form.hora_arribo" type="time" class="w-full border rounded-md px-3 py-2" />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">MUNICIPIO</label>
          <select v-model="form.municipio_arribo" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="Victoria">Victoria</option>
            <option value="Ciudad Mante">Ciudad Mante</option>
            <option value="Matamoros">Matamoros</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">LOCALIDAD</label>
          <input v-model="form.localidad_arribo" class="w-full border rounded-md px-3 py-2" maxlength="150" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">REFERENCIAS</label>
          <textarea v-model="form.referencias_arribo" rows="3" class="w-full border rounded-md px-3 py-2" maxlength="2450"></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">REQUIERE APOYO</label>
          <select v-model="form.requiere_apoyo" class="w-full border rounded-md px-3 py-2">
            <option value="">--SELECCIONE--</option>
            <option value="0">NO</option>
            <option value="1">SI</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">ESPECIFIQUE</label>
          <input v-model="form.especifica_apoyo" class="w-full border rounded-md px-3 py-2" maxlength="200" />
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">ORGANIZACIONES PARTICIPANTES EN EL HECHO</label>
          <div class="flex flex-wrap gap-4 mt-2">
            <label class="flex items-center gap-2"><input type="checkbox" value="PROTECCIÓN CIVIL" v-model="organizaciones" /> PROTECCIÓN CIVIL</label>
            <label class="flex items-center gap-2"><input type="checkbox" value="BOMBEROS" v-model="organizaciones" /> BOMBEROS</label>
            <label class="flex items-center gap-2"><input type="checkbox" value="URGENCIAS MÉDICAS" v-model="organizaciones" /> URGENCIAS MÉDICAS</label>
          </div>
        </div>

        <div class="md:col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">ESPECIFIQUE</label>
          <input v-model="form.especifica_organizacion" class="w-full border rounded-md px-3 py-2" maxlength="200" />
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
import { ref, onMounted, watch } from "vue";
import api from "../../store/api";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar"]);

const organizaciones = ref([]);
const guardando = ref(false);
const form = ref({
  tipo_evento: "",
  medio_noticia: "",
  especifica_noticia: "",
  tipo_delito: "",
  fecha_arribo: "",
  hora_arribo: "00:00",
  municipio_arribo: "",
  localidad_arribo: "",
  referencias_arribo: "",
  requiere_apoyo: "",
  especifica_apoyo: "",
  organizaciones_participantes: "",
  especifica_organizacion: "",
});

watch(organizaciones, (value) => {
  form.value.organizaciones_participantes = value.join(" | ");
}, { immediate: true });

function mapear(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    tipo_evento: data.tipo_evento ?? data.TIPO_EVENTO ?? "",
    medio_noticia: data.medio_noticia ?? data.MEDIO_NOTICIA ?? "",
    especifica_noticia: data.especifica_noticia ?? data.ESPECIFIQUE_NOTICIA ?? "",
    tipo_delito: data.tipo_delito ?? data.TIPO_DELITO ?? "",
    fecha_arribo: data.fecha_arribo ?? data.FECHA_ARRIBO ?? "",
    hora_arribo: data.hora_arribo ?? data.HORA_ARRIBO ?? "00:00",
    municipio_arribo: data.municipio_arribo ?? data.MUNICIPIO_ARRIBO ?? "",
    localidad_arribo: data.localidad_arribo ?? data.LOCALIDAD_ARRIBO ?? "",
    referencias_arribo: data.referencias_arribo ?? data.REFERENCIAS_ARRIBO ?? "",
    requiere_apoyo: data.requiere_apoyo ?? data.REQUIERE_APOYO ?? "",
    especifica_apoyo: data.especifica_apoyo ?? data.ESPECIFIQUE_APOYO ?? "",
    organizaciones_participantes: data.organizaciones_participantes ?? data.ORGANIZACIONES_PARTICIPANTES ?? "",
    especifica_organizacion: data.especifica_organizacion ?? data.ESPECIFIQUE_ORGANIZACION ?? "",
  };

  organizaciones.value = String(form.value.organizaciones_participantes || "")
    .split("|")
    .map((item) => item.trim())
    .filter(Boolean);
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/acta_noticia`);
  mapear(data);
}

async function guardar() {
  guardando.value = true;
  try {
    await api.put(`/iph/${props.iphId}/acta_noticia`, form.value);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

onMounted(cargar);
</script>
