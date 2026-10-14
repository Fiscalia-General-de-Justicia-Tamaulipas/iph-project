<template>
  <form ref="formulario" class="disposicion-form" @submit.prevent="guardar">
    <section class="disposicion-block" aria-labelledby="anexos-titulo">
      <h2 id="anexos-titulo">Apartado 1.1 Fecha y hora de la puesta a disposición</h2>
      <div class="disposicion-metadata">
        <div>
          <label for="disposicion-fecha">Fecha *</label>
          <input id="disposicion-fecha" v-model="form.fecha" type="date" required />
        </div>
        <div>
          <label for="disposicion-hora">Hora * <span>(24 horas)</span></label>
          <input id="disposicion-hora" v-model="form.hora" type="time" required />
        </div>
        <div>
          <label for="disposicion-expediente">No. expediente</label>
          <input id="disposicion-expediente" v-model="form.no_expediente" type="text" maxlength="80" />
        </div>
      </div>
      <div class="disposicion-annex-grid">
        <div
          v-for="anexo in anexos"
          :key="anexo.clave"
          class="disposicion-annex-row"
          :class="{ 'disposicion-annex-row-d': anexo.clave === 'D' }"
        >
          <label :for="`anexo-${anexo.clave}`">
            {{ anexo.nombre }}<span v-if="anexo.obligatorio">*</span>
          </label>
          <select
            :id="`anexo-${anexo.clave}`"
            v-model="form.anexos[anexo.clave].entregado"
            :disabled="form.sin_anexos"
            :aria-label="`${anexo.nombre}: ¿se entrega?`"
            @change="actualizarCadena(anexo.clave, $event.target.value)"
          >
            <option value="NO">NO</option>
            <option value="SI">SI</option>
          </select>
          <template v-if="anexo.clave === 'A' || anexo.clave === 'C' || anexo.clave === 'E'">
            <input
              v-model.number="form.anexos[anexo.clave].cantidad"
              type="number"
              min="0"
              :disabled="form.sin_anexos || form.anexos[anexo.clave].entregado !== 'SI'"
              :aria-label="`Cantidad de registros del anexo ${anexo.clave}`"
            />
          </template>
          <template v-else-if="anexo.clave === 'D'">
            <input
              v-model.number="form.anexos.D.armas"
              type="number"
              min="0"
              :disabled="form.sin_anexos || form.anexos.D.entregado !== 'SI'"
              aria-label="Cantidad de armas"
            />
            <input
              v-model.number="form.anexos.D.objetos"
              type="number"
              min="0"
              :disabled="form.sin_anexos || form.anexos.D.entregado !== 'SI'"
              aria-label="Cantidad de objetos"
            />
          </template>
        </div>
      </div>

      <label class="disposicion-check disposicion-no-annexes">
        <input v-model="form.sin_anexos" type="checkbox" @change="actualizarAnexos" />
        No se entregan Anexos
      </label>

      <div class="disposicion-docs">
        <label for="documentacion-complementaria">¿Anexa documentación complementaria? *</label>
        <select id="documentacion-complementaria" v-model="form.documentacion_complementaria">
          <option value="NO">NO</option>
          <option value="SI">SI</option>
        </select>
        <fieldset :disabled="form.documentacion_complementaria !== 'SI'">
          <legend>Seleccione el tipo de documentación</legend>
          <label v-for="documento in tiposDocumentacion" :key="documento" class="disposicion-check">
            <input v-model="form.tipos_documentacion" type="checkbox" :value="documento" />
            {{ documento }}
          </label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block" aria-labelledby="entrega-titulo">
      <h2 id="entrega-titulo">Datos de quien realiza la puesta a disposición</h2>
      <div class="disposicion-person-grid">
        <div>
          <label for="responsable-apellido1">Primer apellido *</label>
          <input id="responsable-apellido1" v-model="form.responsable.primer_apellido" required maxlength="100" />
        </div>
        <div>
          <label for="responsable-apellido2">Segundo apellido</label>
          <input id="responsable-apellido2" v-model="form.responsable.segundo_apellido" maxlength="100" />
        </div>
        <div>
          <label for="responsable-nombres">Nombre(s) *</label>
          <input id="responsable-nombres" v-model="form.responsable.nombres" required maxlength="150" />
        </div>
        <div class="disposicion-wide">
          <label for="responsable-adscripcion">Adscripción *</label>
          <input id="responsable-adscripcion" v-model="form.responsable.adscripcion" required maxlength="200" />
        </div>
        <div class="disposicion-wide">
          <label for="responsable-cargo">Cargo/Grado *</label>
          <input id="responsable-cargo" v-model="form.responsable.cargo" required maxlength="120" />
        </div>
        <fieldset class="disposicion-radio-group">
          <legend>Firma *</legend>
          <label><input v-model="form.responsable.firma" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.responsable.firma" type="radio" value="NO" /> No</label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block" aria-labelledby="receptor-titulo">
      <h2 id="receptor-titulo">Fiscal/Autoridad que recibe la puesta a disposición</h2>
      <div class="disposicion-person-grid">
        <div>
          <label for="receptor-apellido1">Primer apellido *</label>
          <input id="receptor-apellido1" v-model="form.receptor.primer_apellido" required maxlength="100" />
        </div>
        <div>
          <label for="receptor-apellido2">Segundo apellido</label>
          <input id="receptor-apellido2" v-model="form.receptor.segundo_apellido" maxlength="100" />
        </div>
        <div>
          <label for="receptor-nombres">Nombre(s) *</label>
          <input id="receptor-nombres" v-model="form.receptor.nombres" required maxlength="150" />
        </div>
        <div class="disposicion-wide">
          <label for="receptor-institucion">Fiscalía/Autoridad *</label>
          <input id="receptor-institucion" v-model="form.receptor.institucion" required maxlength="200" />
        </div>
        <div class="disposicion-wide">
          <label for="receptor-adscripcion">Adscripción *</label>
          <input id="receptor-adscripcion" v-model="form.receptor.adscripcion" required maxlength="200" />
        </div>
        <div class="disposicion-wide">
          <label for="receptor-cargo">Cargo *</label>
          <input id="receptor-cargo" v-model="form.receptor.cargo" required maxlength="120" />
        </div>
        <fieldset class="disposicion-radio-group">
          <legend>Firma *</legend>
          <label><input v-model="form.receptor.firma" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.receptor.firma" type="radio" value="NO" /> No</label>
        </fieldset>
        <fieldset class="disposicion-radio-group">
          <legend>Sello de la institución/autoridad que recibe el formato IPH *</legend>
          <label><input v-model="form.receptor.sello" type="radio" value="SI" required /> Sí</label>
          <label><input v-model="form.receptor.sello" type="radio" value="NO" /> No</label>
        </fieldset>
      </div>
    </section>

    <section class="disposicion-block disposicion-upload" aria-labelledby="archivo-titulo">
      <h2 id="archivo-titulo">Formato IPH</h2>
      <p>
        Primero debe guardar avances. Después puede cargar el documento escaneado del IPH presentado
        ante el MP, firmado y sellado. Tamaño máximo: 50 MB.
      </p>
      <div class="disposicion-file-controls">
        <button
          type="button"
          class="disposicion-save-button"
          :disabled="!avancesGuardados"
          @click="selectorArchivo?.click()"
        >
          CARGAR ARCHIVO
        </button>
        <input
          ref="selectorArchivo"
          class="disposicion-file-input"
          type="file"
          hidden
          accept=".pdf,.jpg,.jpeg,.png,.doc,.docx,.mp3,.mp4,.mpeg,.mpg,.wav"
          aria-label="Seleccionar archivo del formato IPH"
          @change="agregarArchivo"
        />
      </div>
      <p v-if="errorArchivo" class="disposicion-error" role="alert">{{ errorArchivo }}</p>
      <table class="disposicion-file-table">
        <thead>
          <tr><th>Archivo</th><th>Tipo Archivo</th><th>Eliminar</th><th>Descargar</th></tr>
        </thead>
        <tbody>
          <tr v-for="archivo in archivos" :key="archivo.id">
            <td>{{ archivo.file.name }}</td>
            <td>{{ archivo.file.type || extension(archivo.file.name) }}</td>
            <td><button type="button" class="disposicion-text-button" @click="eliminarArchivo(archivo.id)">Eliminar</button></td>
            <td><button type="button" class="disposicion-text-button" @click="descargarArchivo(archivo)">Descargar</button></td>
          </tr>
          <tr v-if="!archivos.length"><td colspan="4">No se ha cargado un archivo en esta sesión.</td></tr>
        </tbody>
      </table>
    </section>

    <p class="disposicion-test-note">
      Modo de prueba: los campos se guardan en este navegador. Los archivos solo permanecen mientras esta pantalla esté abierta.
    </p>
    <p v-if="mensaje" class="disposicion-success" role="status">{{ mensaje }}</p>
    <p v-if="errorGuardado" class="disposicion-error" role="alert">{{ errorGuardado }}</p>

    <footer class="disposicion-actions">
      <button type="submit" class="disposicion-save-button">GUARDAR AVANCES</button>
      <button type="button" class="disposicion-next-button" aria-label="Guardar avances y continuar a la sección 2" @click="guardarYSiguiente">
        <span aria-hidden="true">➜</span>
      </button>
    </footer>
  </form>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  iph: { type: Object, default: null },
});
const emit = defineEmits(["siguiente", "anexos-actualizados"]);

const anexos = [
  { clave: "A", nombre: "Anexo A. Detención(es)", obligatorio: true },
  { clave: "B", nombre: "Anexo B. Informe del uso de la fuerza", obligatorio: true },
  { clave: "C", nombre: "Anexo C. Inspección de vehículo", obligatorio: true },
  { clave: "D", nombre: "Anexo D. Inventario de armas y objetos", obligatorio: true },
  { clave: "E", nombre: "Anexo E. Entrevistas", obligatorio: true },
  { clave: "F", nombre: "Anexo F. Entrega-recepción del lugar de intervención", obligatorio: true },
];
const tiposDocumentacion = ["Fotografías", "Videos", "Audio", "Certificados médicos", "Otra"];
const formulario = ref(null);
const selectorArchivo = ref(null);
const archivos = ref([]);
const avancesGuardados = ref(false);
const errorArchivo = ref("");
const errorGuardado = ref("");
const mensaje = ref("");

function crearBorrador() {
  return {
    fecha: "",
    hora: "",
    no_expediente: props.iph?.no_expediente || "",
    sin_anexos: false,
    anexos: {
      A: { entregado: "NO", cantidad: 0 },
      B: { entregado: "NO", cantidad: 0 },
      C: { entregado: "NO", cantidad: 0 },
      D: { entregado: "NO", armas: 0, objetos: 0 },
      E: { entregado: "NO", cantidad: 0 },
      F: { entregado: "NO", cantidad: 0 },
    },
    documentacion_complementaria: "NO",
    tipos_documentacion: [],
    responsable: {
      primer_apellido: "",
      segundo_apellido: "",
      nombres: "",
      adscripcion: "",
      cargo: "",
      firma: "",
    },
    receptor: {
      primer_apellido: "",
      segundo_apellido: "",
      nombres: "",
      institucion: "",
      adscripcion: "",
      cargo: "",
      firma: "",
      sello: "",
    },
  };
}

const form = ref(crearBorrador());
const claveBorrador = () => `iph-pruebas:${props.iphId}:puesta_disposicion`;

function notificarAnexos() {
  const entregados = Object.fromEntries(
    anexos.map(({ clave }) => [clave, !form.value.sin_anexos && form.value.anexos[clave].entregado === "SI"]),
  );
  emit("anexos-actualizados", entregados);
}

function limpiarAnexo(anexo) {
  form.value.anexos[anexo.clave].entregado = "NO";
  if ("cantidad" in form.value.anexos[anexo.clave]) form.value.anexos[anexo.clave].cantidad = 0;
  if (anexo.clave === "D") {
    form.value.anexos.D.armas = 0;
    form.value.anexos.D.objetos = 0;
  }
}

function normalizarCadena() {
  for (let index = 0; index < anexos.length - 1; index += 1) {
    if (form.value.anexos[anexos[index].clave].entregado !== "SI") {
      for (const anexoSiguiente of anexos.slice(index + 1)) limpiarAnexo(anexoSiguiente);
      break;
    }
  }
}

function cargarBorrador() {
  errorGuardado.value = "";
  let guardado;
  try {
    guardado = localStorage.getItem(claveBorrador());
    if (guardado === null) {
      form.value = crearBorrador();
      avancesGuardados.value = false;
      notificarAnexos();
      return;
    }
    const datos = JSON.parse(guardado);
    if (!datos || typeof datos !== "object" || Array.isArray(datos)) {
      throw new Error("El borrador guardado no tiene un formato válido.");
    }
    const base = crearBorrador();
    form.value = {
      ...base,
      ...datos,
      anexos: { ...base.anexos, ...(datos.anexos || {}) },
      responsable: { ...base.responsable, ...(datos.responsable || {}) },
      receptor: { ...base.receptor, ...(datos.receptor || {}) },
    };
    normalizarCadena();
    avancesGuardados.value = true;
    notificarAnexos();
  } catch (error) {
    avancesGuardados.value = false;
    errorGuardado.value = `No se pudo cargar el borrador local: ${error.message}`;
  }
}

function guardar() {
  errorGuardado.value = "";
  mensaje.value = "";
  try {
    localStorage.setItem(claveBorrador(), JSON.stringify(form.value));
    avancesGuardados.value = true;
    mensaje.value = "Avances guardados en este navegador.";
    return true;
  } catch (error) {
    avancesGuardados.value = false;
    errorGuardado.value = `No se pudieron guardar los avances: ${error.message}`;
    return false;
  }
}

function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  if (guardar()) emit("siguiente");
}

function actualizarAnexos() {
  if (!form.value.sin_anexos) return;
  for (const anexo of anexos) limpiarAnexo(anexo);
  notificarAnexos();
}

function actualizarCadena(clave, valorSeleccionado) {
  if (valorSeleccionado !== "SI") {
    const index = anexos.findIndex((anexo) => anexo.clave === clave);
    for (const anexoSiguiente of anexos.slice(index + 1)) limpiarAnexo(anexoSiguiente);
  }
  notificarAnexos();
}

function agregarArchivo(event) {
  errorArchivo.value = "";
  const seleccionados = Array.from(event.target.files || []);
  for (const file of seleccionados) {
    if (file.size > 50 * 1024 * 1024) {
      errorArchivo.value = `${file.name} excede el tamaño máximo de 50 MB.`;
      continue;
    }
    archivos.value.push({ id: `${Date.now()}-${Math.random()}`, file });
  }
  event.target.value = "";
}

function eliminarArchivo(id) {
  archivos.value = archivos.value.filter((archivo) => archivo.id !== id);
}

function descargarArchivo(archivo) {
  const url = URL.createObjectURL(archivo.file);
  const enlace = document.createElement("a");
  enlace.href = url;
  enlace.download = archivo.file.name;
  enlace.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function extension(nombre) {
  return nombre.split(".").pop()?.toUpperCase() || "Archivo";
}

watch(() => props.iphId, cargarBorrador);
watch(() => props.iph?.no_expediente, (noExpediente) => {
  if (noExpediente && !form.value.no_expediente) form.value.no_expediente = noExpediente;
});
onMounted(cargarBorrador);
</script>
