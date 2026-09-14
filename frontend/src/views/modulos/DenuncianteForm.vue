<template>
  <div class="bg-white rounded-lg shadow p-6 max-w-5xl">
    <h2 class="font-semibold text-lg mb-4 text-gray-800">{{ titulo }}</h2>

    <div class="divide-y mb-6">
      <div v-for="d in lista" :key="d.id" class="py-3 flex justify-between items-center">
        <div>
          <p class="font-medium">{{ d.primer_apellido }} {{ d.segundo_apellido }} {{ d.nombres }}</p>
          <p class="text-xs text-gray-500">{{ d.telefono || "Sin teléfono" }} · {{ d.nacionalidad || "Sin nacionalidad" }}</p>
        </div>
        <button @click="eliminar(d.id)" class="text-red-500 text-sm hover:underline">Eliminar</button>
      </div>
      <p v-if="lista.length === 0" class="text-gray-400 text-sm py-2">Aún no hay denunciantes capturados.</p>
    </div>

    <h3 class="font-medium text-gray-700 mb-3">Agregar {{ etiqueta }}</h3>
    <form @submit.prevent="agregar" class="grid md:grid-cols-2 gap-4">
      <div class="md:col-span-2">
        <div class="grid md:grid-cols-2 gap-4">
          <div v-for="bloque in bloquesExtra" :key="bloque.key" class="border rounded-md p-3 bg-gray-50">
            <div class="flex items-center justify-between mb-2">
              <label class="text-sm font-medium text-gray-700">{{ bloque.label }}</label>
              <button type="button" @click="agregarItem(bloque.key)" class="text-xs bg-institucional-verde text-white px-2 py-1 rounded">Agregar</button>
            </div>
            <div class="space-y-2">
              <div v-for="(item, idx) in form[bloque.key]" :key="`${bloque.key}-${idx}`" class="flex gap-2">
                <input v-model="form[bloque.key][idx]" class="border rounded-md px-3 py-2 w-full text-sm" placeholder="Escribe un valor" />
                <button type="button" @click="quitarItem(bloque.key, idx)" class="text-red-500 text-sm">×</button>
              </div>
              <p v-if="!form[bloque.key].length" class="text-xs text-gray-400">Sin elementos agregados.</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">PRIMER APELLIDO</label>
        <input v-model="form.primer_apellido" class="border rounded-md px-3 py-2 w-full" />
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">SEGUNDO APELLIDO</label>
        <input v-model="form.segundo_apellido" class="border rounded-md px-3 py-2 w-full" />
      </div>
      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">NOMBRE(S)</label>
        <input v-model="form.nombres" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">SEXO</label>
        <select v-model="form.sexo" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="HOMBRE">HOMBRE</option>
          <option value="MUJER">MUJER</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NACIONALIDAD</label>
        <select v-model="form.nacionalidad" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="MEXICANA">MEXICANA</option>
          <option value="EXTRANJERA">EXTRANJERA</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">FECHA DE NACIMIENTO</label>
        <input v-model="form.fecha_nacimiento" type="date" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">EDAD</label>
        <input v-model.number="form.edad" type="number" min="0" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">TIPO DE DOCUMENTO</label>
        <select v-model="form.tipo_documento" class="border rounded-md px-3 py-2 w-full">
          <option value="">--SELECCIONE--</option>
          <option value="INE">INE</option>
          <option value="CREDENCIAL">Credencial</option>
          <option value="PASAPORTE">Pasaporte</option>
          <option value="LICENCIA">Licencia</option>
          <option value="OTRO">Otro</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NÚMERO DE IDENTIFICACIÓN</label>
        <input v-model="form.no_identificacion" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">TELÉFONO</label>
        <input v-model="form.telefono" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">CORREO</label>
        <input v-model="form.correo" type="email" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">CALLE / TRAMO</label>
        <input v-model="form.calle_tramo" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NO. EXTERIOR</label>
        <input v-model="form.no_exterior" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">NO. INTERIOR</label>
        <input v-model="form.no_interior" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">CÓDIGO POSTAL</label>
        <input v-model="form.codigo_postal" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">COLONIA / LOCALIDAD</label>
        <input v-model="form.colonia_localidad" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">MUNICIPIO</label>
        <input v-model="form.municipio" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ENTIDAD FEDERATIVA</label>
        <input v-model="form.entidad_federativa" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">ESTATURA</label>
        <input v-model="form.estatura" class="border rounded-md px-3 py-2 w-full" placeholder="1.70 m" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">COMPLEXIÓN</label>
        <input v-model="form.complexion" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">COMPLEXIONES</label>
        <input v-model="form.complexiones" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">COLOR DE OJOS</label>
        <input v-model="form.color_ojos" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 mb-1">COLOR DE PELO</label>
        <input v-model="form.color_pelo" class="border rounded-md px-3 py-2 w-full" />
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">REFERENCIAS</label>
        <textarea v-model="form.referencias" rows="3" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">CICATRICES</label>
        <textarea v-model="form.cicatrices" rows="2" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">TATUAJES</label>
        <textarea v-model="form.tatuajes" rows="2" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">PERFORACIONES</label>
        <textarea v-model="form.perforaciones" rows="2" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">OTROS RASGOS</label>
        <textarea v-model="form.otros_rasgos" rows="2" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <div class="md:col-span-2">
        <label class="block text-sm font-medium text-gray-700 mb-1">RELATO</label>
        <textarea v-model="form.relato" rows="3" class="border rounded-md px-3 py-2 w-full"></textarea>
      </div>

      <button
        type="submit"
        :disabled="guardando"
        class="md:col-span-2 bg-institucional-verde text-white px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
      >
        {{ guardando ? "Agregando..." : `Agregar ${etiqueta}` }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../../store/api";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  tipo: { type: String, default: "denunciante" },
});
const emit = defineEmits(["guardado"]);

const tipoConfig = {
  denunciante: { titulo: "Denunciante(s)", etiqueta: "denunciante", plural: "denunciantes" },
  ofendido: { titulo: "Ofendido(s)", etiqueta: "ofendido", plural: "ofendidos" },
  victima: { titulo: "Víctima(s)", etiqueta: "víctima", plural: "victimas" },
  imputado: { titulo: "Imputado(s)", etiqueta: "imputado", plural: "imputados" },
  testigo: { titulo: "Testigo(s)", etiqueta: "testigo", plural: "testigos" },
};

const titulo = computed(() => tipoConfig[props.tipo]?.titulo || tipoConfig.denunciante.titulo);
const etiqueta = computed(() => tipoConfig[props.tipo]?.etiqueta || tipoConfig.denunciante.etiqueta);

const entidad = computed(() => tipoConfig[props.tipo]?.plural || "denunciantes");

const bloquesExtra = [
  { key: "alias", label: "Alias / apodos" },
  { key: "vestimenta", label: "Vestimenta" },
  { key: "huellas", label: "Huellas" },
  { key: "senas_particulares", label: "Señas particulares" },
];

const lista = ref([]);
const guardando = ref(false);
const form = ref({
  primer_apellido: "",
  segundo_apellido: "",
  nombres: "",
  sexo: "",
  nacionalidad: "",
  fecha_nacimiento: "",
  edad: "",
  tipo_documento: "",
  no_identificacion: "",
  telefono: "",
  correo: "",
  calle_tramo: "",
  no_exterior: "",
  no_interior: "",
  codigo_postal: "",
  colonia_localidad: "",
  municipio: "",
  entidad_federativa: "",
  referencias: "",
  estatura: "",
  complexion: "",
  complexiones: "",
  color_ojos: "",
  color_pelo: "",
  cicatrices: "",
  tatuajes: "",
  perforaciones: "",
  otros_rasgos: "",
  relato: "",
  alias: [],
  vestimenta: [],
  huellas: [],
  senas_particulares: [],
});

function agregarItem(key) {
  form.value[key].push("");
}

function quitarItem(key, idx) {
  form.value[key].splice(idx, 1);
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/${entidad.value}/lista`);
  lista.value = data || [];
}

async function agregar() {
  guardando.value = true;
  try {
    const payload = { ...form.value };
    await api.post(`/iph/${props.iphId}/${entidad.value}/lista`, payload);
    form.value = {
      primer_apellido: "",
      segundo_apellido: "",
      nombres: "",
      sexo: "",
      nacionalidad: "",
      fecha_nacimiento: "",
      edad: "",
      tipo_documento: "",
      no_identificacion: "",
      telefono: "",
      correo: "",
      calle_tramo: "",
      no_exterior: "",
      no_interior: "",
      codigo_postal: "",
      colonia_localidad: "",
      municipio: "",
      entidad_federativa: "",
      referencias: "",
      estatura: "",
      complexion: "",
      complexiones: "",
      color_ojos: "",
      color_pelo: "",
      cicatrices: "",
      tatuajes: "",
      perforaciones: "",
      otros_rasgos: "",
      relato: "",
      alias: [],
      vestimenta: [],
      huellas: [],
      senas_particulares: [],
    };
    await cargar();
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function eliminar(id) {
  await api.delete(`/iph/${props.iphId}/${entidad.value}/lista/${id}`);
  await cargar();
  emit("guardado");
}

onMounted(cargar);
</script>
