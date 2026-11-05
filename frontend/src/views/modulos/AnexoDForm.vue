<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>
    <section class="test-module-section">
      <header class="test-module-section-heading"><h2>ANEXO D. INVENTARIO DE ARMAS Y OBJETOS</h2><span>Campo obligatorio*</span></header>
      <p class="annex-pad annex-instruction">Llene tantas veces como sea necesario este Anexo.</p>
      <header class="test-module-section-heading"><h2>Apartado D.1 Registro de armas de fuego</h2><button type="button" class="test-module-primary" @click="abrirArma()">Nueva arma</button></header>
      <div class="test-module-table-wrap"><table class="test-module-table">
        <thead><tr><th>Consecutivo de arma</th><th>Tipo de arma</th><th>Calibre</th><th>Color</th><th>Matrícula</th><th>No. serie</th><th>Editar</th><th>Eliminar</th></tr></thead>
        <tbody><tr v-if="!armas.length"><td colspan="8">No hay información a mostrar</td></tr>
          <tr v-for="(arma, index) in armas" :key="arma.id"><td>{{ consecutivo(index) }}</td><td>{{ arma.tipo_arma }}</td><td>{{ arma.calibre }}</td><td>{{ arma.color }}</td><td>{{ arma.matricula }}</td><td>{{ arma.serie }}</td><td><button class="test-module-remove" type="button" @click="abrirArma(arma.id)">Editar</button></td><td><button class="test-module-remove" type="button" @click="eliminarArma(arma.id)">Eliminar</button></td></tr>
        </tbody></table></div>
    </section>

    <section v-if="armaAbierta" class="test-module-section">
      <header class="test-module-section-heading"><h2>{{ armaActual.id ? "Editar arma" : "Registro de arma de fuego" }}</h2></header>
      <div class="test-module-form-body">
        <p class="annex-instruction">Para agregar imágenes relacionadas a la(s) arma(s) decomisada(s), primero capture los datos y guarde el registro.</p>
        <div class="test-module-grid">
          <label class="test-module-field"><span>Arma de fuego</span><input :value="consecutivo(armaEditando)" readonly /></label>
          <fieldset class="test-module-field"><legend>Seleccione si se trata de aportación o inspección *</legend><label class="test-module-check"><input v-model="armaActual.origen" type="radio" value="Aportación" /> Aportación</label><label class="test-module-check"><input v-model="armaActual.origen" type="radio" value="Inspección" /> Inspección</label></fieldset>
          <label class="test-module-field"><span>Tipo de arma *</span><select v-model="armaActual.tipo_arma" required><option value="">- - - -</option><option>CORTA</option><option>LARGA</option></select></label>
          <label class="test-module-field"><span>¿Dónde se encontró el arma?</span><textarea v-model="armaActual.ubicacion" rows="2" placeholder="¿DÓNDE SE ENCONTRÓ EL ARMA?" /></label>
          <label class="test-module-field"><span>Calibre</span><input v-model="armaActual.calibre" placeholder="CALIBRE" /></label>
          <label class="test-module-field"><span>Color</span><input v-model="armaActual.color" placeholder="COLOR" /></label>
          <label class="test-module-field"><span>Matrícula</span><input v-model="armaActual.matricula" placeholder="MATRÍCULA" /></label>
          <label class="test-module-field"><span>No. de serie</span><input v-model="armaActual.serie" placeholder="NO. DE SERIE" /></label>
          <label class="test-module-field test-module-field-wide"><span>Observaciones (de ser el caso, señale detalles, características, marca, cargadores y cartuchos)</span><textarea v-model="armaActual.observaciones" rows="3" placeholder="OBSERVACIONES" /></label>
          <label class="test-module-field test-module-field-wide"><span>Destino que se le dio *</span><textarea v-model="armaActual.destino" rows="2" required placeholder="DESTINO QUE SE LE DIO" /></label>
        </div>
        <p class="annex-instruction">Anote el nombre y firma de la persona a la que se le aseguró el arma:</p>
        <div class="test-module-grid annex-witness-grid">
          <label class="test-module-field"><span>Primer apellido</span><input v-model="armaActual.persona.primer_apellido" placeholder="PRIMER APELLIDO" /></label>
          <label class="test-module-field"><span>Segundo apellido</span><input v-model="armaActual.persona.segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
          <label class="test-module-field"><span>Nombre(s)</span><input v-model="armaActual.persona.nombres" placeholder="NOMBRE(S)" /></label>
          <label class="test-module-check"><input v-model="armaActual.persona.firma" type="checkbox" /> Firma</label>
        </div>
        <p class="annex-instruction">En caso de que la persona a la que se le aseguró el arma no acceda a firmar, anote nombre y firma de dos testigos.</p>
        <div v-for="(testigo, index) in armaActual.testigos" :key="index" class="test-module-grid annex-witness-grid">
          <label class="test-module-field"><span>Primer apellido</span><input v-model="testigo.primer_apellido" placeholder="PRIMER APELLIDO" /></label>
          <label class="test-module-field"><span>Segundo apellido</span><input v-model="testigo.segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
          <label class="test-module-field"><span>Nombre(s)</span><input v-model="testigo.nombres" placeholder="NOMBRE(S)" /></label>
          <label class="test-module-check"><input v-model="testigo.firma" type="checkbox" /> Firma</label>
        </div>
        <div class="test-module-actions"><button type="button" class="test-module-secondary" @click="agregarTestigo(armaActual)">Agregar testigo</button></div>
      </div>
      <header class="test-module-section-heading"><h2>Apartado D.1.1 Imágenes del arma o armas aseguradas</h2></header>
      <div class="test-module-form-body">
        <p class="annex-instruction">Primero guarde el arma. Se permiten imágenes JPG, JPEG o BMP de hasta 50 MB.</p>
        <div class="annex-upload"><input ref="armaFileInput" type="file" accept=".jpg,.jpeg,.bmp,image/jpeg,image/bmp" :disabled="!armaActual.id" @change="cargarImagen($event, 'arma', armaActual.id)" /><button type="button" class="test-module-secondary" :disabled="!armaActual.id" @click="armaFileInput?.click()">Cargar archivo</button></div>
        <ul class="annex-file-list"><li v-for="file in imagenesArma" :key="file.id"><span>{{ file.name }}</span><button class="test-module-remove" type="button" @click="descargar(file.id)">Descargar</button><button class="test-module-remove" type="button" @click="eliminarArchivo(file.id)">Eliminar</button></li></ul>
      </div>
      <div class="test-module-form-body">
        <label class="test-module-check annex-check"><input v-model="respondiente.seleccionar_seccion1" type="checkbox" @change="copiarRespondiente(respondiente)" /> Seleccione Primer Respondiente de la Sección 1</label>
        <header class="test-module-section-heading"><h2>Apartado D.2 Datos del primer respondiente que realizó la recolección y/o aseguramiento del arma</h2></header>
        <div class="test-module-grid">
          <label class="test-module-field"><span>Primer apellido *</span><input v-model="respondiente.primer_apellido" required /></label>
          <label class="test-module-field"><span>Segundo apellido</span><input v-model="respondiente.segundo_apellido" /></label>
          <label class="test-module-field"><span>Nombre(s) *</span><input v-model="respondiente.nombres" required /></label>
          <label class="test-module-field"><span>Adscripción *</span><input v-model="respondiente.adscripcion" required /></label>
          <label class="test-module-field"><span>Cargo / grado *</span><input v-model="respondiente.cargo" required /></label>
          <label class="test-module-check"><input v-model="respondiente.firma" type="checkbox" /> Firma</label>
        </div>
        <div class="test-module-actions"><button type="button" class="test-module-primary" @click="guardarArma">Guardar arma</button></div>
      </div>
    </section>

    <section class="test-module-section">
      <header class="test-module-section-heading"><h2>Apartado D.3 Registro de objetos recolectados y/o asegurados relacionados con el hecho probablemente delictivo</h2><button type="button" class="test-module-primary" @click="abrirObjeto()">Nuevo objeto</button></header>
      <div class="test-module-table-wrap"><table class="test-module-table"><thead><tr><th>Consecutivo de objeto</th><th>Apariencia de</th><th>Breve descripción</th><th>Editar</th><th>Eliminar</th></tr></thead>
        <tbody><tr v-if="!objetos.length"><td colspan="5">No hay información a mostrar</td></tr><tr v-for="(objeto, index) in objetos" :key="objeto.id"><td>{{ consecutivo(index) }}</td><td>{{ objeto.apariencia }}</td><td>{{ objeto.descripcion }}</td><td><button class="test-module-remove" type="button" @click="abrirObjeto(objeto.id)">Editar</button></td><td><button class="test-module-remove" type="button" @click="eliminarObjeto(objeto.id)">Eliminar</button></td></tr></tbody>
      </table></div>
    </section>

    <section v-if="objetoAbierto" class="test-module-section">
      <header class="test-module-section-heading"><h2>{{ objetoActual.id ? "Editar objeto" : "Registro de objeto recolectado y/o asegurado" }}</h2></header>
      <div class="test-module-form-body">
        <p class="annex-instruction">Para agregar imágenes relacionadas al objeto u objetos decomisados, primero capture y guarde la información.</p>
        <div class="test-module-grid">
          <label class="test-module-field"><span>Objeto</span><input :value="consecutivo(objetoEditando)" readonly /></label>
          <label class="test-module-field"><span>¿Qué encontró? (apariencia de) *</span><select v-model="objetoActual.apariencia" required><option value="">- - - -</option><option>HIDROCARBURO</option><option>NUMERARIO</option><option>NARCÓTICO</option><option>OTRO</option></select></label>
          <label v-if="objetoActual.apariencia === 'OTRO'" class="test-module-field"><span>Especifique</span><input v-model="objetoActual.apariencia_otro" /></label>
          <fieldset class="test-module-field"><legend>Seleccione si se trata de aportación o inspección *</legend><label class="test-module-check"><input v-model="objetoActual.origen" type="radio" value="Aportación" /> Aportación</label><label class="test-module-check"><input v-model="objetoActual.origen" type="radio" value="Inspección" /> Inspección</label></fieldset>
          <label v-if="objetoActual.origen === 'Inspección'" class="test-module-field"><span>Tipo de inspección *</span><select v-model="objetoActual.tipo_inspeccion"><option value="">- - - -</option><option>LUGAR</option><option>PERSONA</option><option>VEHÍCULO</option></select></label>
          <label class="test-module-field"><span>¿Dónde se encontró el objeto?</span><textarea v-model="objetoActual.ubicacion" rows="2" placeholder="¿DÓNDE SE ENCONTRÓ EL OBJETO?" /></label>
          <label class="test-module-field test-module-field-wide"><span>Breve descripción del objeto</span><textarea v-model="objetoActual.descripcion" rows="3" placeholder="BREVE DESCRIPCIÓN DEL OBJETO" /></label>
          <label class="test-module-field test-module-field-wide"><span>Destino que se le dio</span><textarea v-model="objetoActual.destino" rows="2" placeholder="DESTINO QUE SE LE DIO" /></label>
        </div>
        <p class="annex-instruction">Anote el nombre y firma de la persona a la que se le aseguró el objeto:</p>
        <div class="test-module-grid annex-witness-grid">
          <label class="test-module-field"><span>Primer apellido</span><input v-model="objetoActual.persona.primer_apellido" placeholder="PRIMER APELLIDO" /></label><label class="test-module-field"><span>Segundo apellido</span><input v-model="objetoActual.persona.segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label><label class="test-module-field"><span>Nombre(s)</span><input v-model="objetoActual.persona.nombres" placeholder="NOMBRE(S)" /></label><label class="test-module-check"><input v-model="objetoActual.persona.firma" type="checkbox" /> Firma</label>
        </div>
        <p class="annex-instruction">En caso de que la persona no acceda a firmar, anote nombre y firma de dos testigos.</p>
        <div v-for="(testigo, index) in objetoActual.testigos" :key="index" class="test-module-grid annex-witness-grid">
          <label class="test-module-field"><span>Primer apellido</span><input v-model="testigo.primer_apellido" placeholder="PRIMER APELLIDO" /></label><label class="test-module-field"><span>Segundo apellido</span><input v-model="testigo.segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label><label class="test-module-field"><span>Nombre(s)</span><input v-model="testigo.nombres" placeholder="NOMBRE(S)" /></label><label class="test-module-check"><input v-model="testigo.firma" type="checkbox" /> Firma</label>
        </div>
        <div class="test-module-actions"><button type="button" class="test-module-secondary" @click="agregarTestigo(objetoActual)">Agregar testigo</button></div>
      </div>
      <header class="test-module-section-heading"><h2>Apartado D.3.1 Imágenes del objeto u objetos asegurados</h2></header>
      <div class="test-module-form-body">
        <p class="annex-instruction">Se permiten imágenes JPG, JPEG o BMP de hasta 50 MB.</p>
        <div class="annex-upload"><input ref="objetoFileInput" type="file" accept=".jpg,.jpeg,.bmp,image/jpeg,image/bmp" :disabled="!objetoActual.id" @change="cargarImagen($event, 'objeto', objetoActual.id)" /><button type="button" class="test-module-secondary" :disabled="!objetoActual.id" @click="objetoFileInput?.click()">Cargar archivo</button></div>
        <ul class="annex-file-list"><li v-for="file in imagenesObjeto" :key="file.id"><span>{{ file.name }}</span><button class="test-module-remove" type="button" @click="descargar(file.id)">Descargar</button><button class="test-module-remove" type="button" @click="eliminarArchivo(file.id)">Eliminar</button></li></ul>
      </div>
      <div class="test-module-form-body">
        <label class="test-module-check annex-check"><input v-model="respondiente.seleccionar_seccion1" type="checkbox" @change="copiarRespondiente(respondiente)" /> Seleccione Primer Respondiente de la Sección 1</label>
        <header class="test-module-section-heading"><h2>Apartado D.4 Datos del primer respondiente que realizó la recolección y/o aseguramiento del objeto</h2></header>
        <div class="test-module-grid">
          <label class="test-module-field"><span>Primer apellido *</span><input v-model="respondiente.primer_apellido" required /></label><label class="test-module-field"><span>Segundo apellido</span><input v-model="respondiente.segundo_apellido" /></label><label class="test-module-field"><span>Nombre(s) *</span><input v-model="respondiente.nombres" required /></label><label class="test-module-field"><span>Adscripción *</span><input v-model="respondiente.adscripcion" required /></label><label class="test-module-field"><span>Cargo / grado *</span><input v-model="respondiente.cargo" required /></label><label class="test-module-check"><input v-model="respondiente.firma" type="checkbox" /> Firma</label>
        </div>
        <p class="annex-instruction">Nota: Este Anexo no sustituye la Cadena de Custodia, la cual deberá ser debidamente requisitada.</p>
        <div class="test-module-actions"><button type="button" class="test-module-primary" @click="guardarObjeto">Guardar objeto</button><button type="button" class="test-module-next" aria-label="Guardar e ir al siguiente anexo" @click="guardarYSiguiente">➜</button></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";
import { eliminarAdjunto, guardarAdjunto, listarAdjuntos, obtenerAdjunto } from "../../store/attachments";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "siguiente"]);
const armas = ref([]);
const objetos = ref([]);
const armaEditando = ref("");
const objetoEditando = ref("");
const armaActual = ref(crearRegistro());
const objetoActual = ref(crearRegistro(true));
const armaAbierta = ref(false);
const objetoAbierto = ref(false);
const error = ref("");
const mensaje = ref("");
const armaFileInput = ref(null);
const objetoFileInput = ref(null);
const imagenesArma = ref([]);
const imagenesObjeto = ref([]);
const respondiente = ref(crearRespondiente());

function crearPersona() { return { primer_apellido: "", segundo_apellido: "", nombres: "", firma: false }; }
function crearRespondiente() { return { primer_apellido: "", segundo_apellido: "", nombres: "", adscripcion: "", cargo: "", firma: false, seleccionar_seccion1: false }; }
function crearRegistro(objeto = false) {
  return {
    id: "", origen: "", tipo_arma: "", calibre: "", color: "", matricula: "", serie: "", ubicacion: "",
    observaciones: "", destino: "", persona: crearPersona(), testigos: [crearPersona(), crearPersona()],
    apariencia: "", apariencia_otro: "", tipo_inspeccion: "", descripcion: "", respondiente: crearRespondiente(),
    ...(objeto ? {} : {}),
  };
}
function consecutivo(index) { return String((Number(index) || 0) + 1).padStart(3, "0"); }
async function cargar() {
  try {
    const saved = await leerCaptura(props.iphId, "anexo_d", `iph-anexo-d:${props.iphId}`) || {};
    armas.value = Array.isArray(saved.armas) ? saved.armas : [];
    objetos.value = Array.isArray(saved.objetos) ? saved.objetos : [];
  } catch (exception) {
    console.error("No se pudieron leer los datos del Anexo D:", exception);
    error.value = "No se pudieron leer los datos guardados del Anexo D.";
  }
}
async function guardarDatos() {
  await guardarCaptura(props.iphId, "anexo_d", { armas: armas.value, objetos: objetos.value });
}
function abrirArma(id = "") {
  armaEditando.value = id;
  armaActual.value = id ? structuredClone(armas.value.find((item) => item.id === id)) : crearRegistro();
  respondiente.value = id ? { ...crearRespondiente(), ...armaActual.value.respondiente } : crearRespondiente();
  armaAbierta.value = true;
  objetoAbierto.value = false;
  cargarImagenes("arma", armaActual.value.id);
}
function abrirObjeto(id = "") {
  objetoEditando.value = id;
  objetoActual.value = id ? structuredClone(objetos.value.find((item) => item.id === id)) : crearRegistro(true);
  respondiente.value = id ? { ...crearRespondiente(), ...objetoActual.value.respondiente } : crearRespondiente();
  objetoAbierto.value = true;
  armaAbierta.value = false;
  cargarImagenes("objeto", objetoActual.value.id);
}
async function guardarArma() {
  if (!armaActual.value.origen || !armaActual.value.tipo_arma || !armaActual.value.destino
    || !respondiente.value.primer_apellido || !respondiente.value.nombres
    || !respondiente.value.adscripcion || !respondiente.value.cargo) {
    error.value = "Complete los campos obligatorios de la captura del arma y del primer respondiente.";
    return;
  }
  const item = { ...armaActual.value, id: armaEditando.value || `${Date.now()}-${Math.random()}`, respondiente: { ...respondiente.value } };
  const index = armas.value.findIndex((arma) => arma.id === item.id);
  if (index < 0) armas.value.push(item);
  else armas.value[index] = item;
  armaEditando.value = item.id;
  armaActual.value = item;
  try {
    await guardarDatos();
    mensaje.value = "Arma guardada en el servidor.";
    error.value = "";
    cargarImagenes("arma", item.id);
    emit("guardado");
    return true;
  } catch (exception) {
    console.error("No se pudo guardar el arma:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el arma en el servidor.";
    return false;
  }
}
async function guardarObjeto() {
  if (!objetoActual.value.apariencia || !objetoActual.value.origen
    || (objetoActual.value.origen === "Inspección" && !objetoActual.value.tipo_inspeccion)
    || !respondiente.value.primer_apellido || !respondiente.value.nombres
    || !respondiente.value.adscripcion || !respondiente.value.cargo) {
    error.value = "Complete los campos obligatorios del objeto y del primer respondiente.";
    return;
  }
  const item = { ...objetoActual.value, id: objetoEditando.value || `${Date.now()}-${Math.random()}`, respondiente: { ...respondiente.value } };
  const index = objetos.value.findIndex((objeto) => objeto.id === item.id);
  if (index < 0) objetos.value.push(item);
  else objetos.value[index] = item;
  objetoEditando.value = item.id;
  objetoActual.value = item;
  try {
    await guardarDatos();
    mensaje.value = "Objeto guardado en el servidor.";
    error.value = "";
    cargarImagenes("objeto", item.id);
    emit("guardado");
    return true;
  } catch (exception) {
    console.error("No se pudo guardar el objeto:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el objeto en el servidor.";
    return false;
  }
}

async function guardarYSiguiente() {
  error.value = "";
  if (armaAbierta.value && !(await guardarArma())) return;
  if (objetoAbierto.value && !(await guardarObjeto())) return;
  try {
    await guardarDatos();
    emit("siguiente");
  } catch (exception) {
    error.value = exception.response?.data?.msg || "No se pudo guardar el Anexo D en el servidor.";
  }
}
async function eliminarArma(id) {
  armas.value = armas.value.filter((item) => item.id !== id);
  try {
    await guardarDatos();
    const files = await listarAdjuntos(props.iphId, `D-arma-${id}`);
    await Promise.all(files.map((file) => eliminarAdjunto(file.id)));
    if (armaActual.value.id === id) {
      armaAbierta.value = false;
      armaActual.value = crearRegistro();
    }
    await cargarImagenes("arma", armaActual.value.id);
  } catch (exception) {
    console.error("No se pudo eliminar el arma y sus imágenes:", exception);
    error.value = "Se eliminó el arma de la lista, pero no se pudieron limpiar sus imágenes.";
  }
}
async function eliminarObjeto(id) {
  objetos.value = objetos.value.filter((item) => item.id !== id);
  try {
    await guardarDatos();
    const files = await listarAdjuntos(props.iphId, `D-objeto-${id}`);
    await Promise.all(files.map((file) => eliminarAdjunto(file.id)));
    if (objetoActual.value.id === id) {
      objetoAbierto.value = false;
      objetoActual.value = crearRegistro(true);
    }
    await cargarImagenes("objeto", objetoActual.value.id);
  } catch (exception) {
    console.error("No se pudo eliminar el objeto y sus imágenes:", exception);
    error.value = "Se eliminó el objeto de la lista, pero no se pudieron limpiar sus imágenes.";
  }
}
function agregarTestigo(registro) { registro.testigos.push(crearPersona()); }
async function copiarRespondiente(destino) {
  if (!destino.seleccionar_seccion1) return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
    const persona = data.find((item) => item.es_primer_respondiente) || data[0];
    if (!persona) throw new Error("No hay primer respondiente registrado en la Sección 1.");
    Object.assign(respondiente.value, {
      primer_apellido: persona.primer_apellido || persona.paterno || "",
      segundo_apellido: persona.segundo_apellido || persona.materno || "",
      nombres: persona.nombres || persona.nombre || "",
      adscripcion: persona.institucion_otra || persona.institucion || "",
      cargo: persona.grado_cargo || "",
      firma: true,
    });
  } catch (exception) {
    console.error("No se pudo cargar el primer respondiente:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente.";
    destino.seleccionar_seccion1 = false;
  }
}
async function cargarImagenes(tipo, id) {
  if (!id) {
    if (tipo === "arma") imagenesArma.value = [];
    else imagenesObjeto.value = [];
    return;
  }
  try {
    const archivos = await listarAdjuntos(props.iphId, `D-${tipo}-${id}`);
    if (tipo === "arma") imagenesArma.value = archivos;
    else imagenesObjeto.value = archivos;
  } catch (exception) {
    console.error("No se pudieron leer las imágenes del Anexo D:", exception);
    error.value = "No se pudieron leer las imágenes guardadas.";
  }
}
async function cargarImagen(event, tipo, id) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (!/\.(jpe?g|bmp)$/i.test(file.name) || file.size > 50 * 1024 * 1024) {
    error.value = "Seleccione una imagen JPG, JPEG o BMP de hasta 50 MB.";
    event.target.value = "";
    return;
  }
  try {
    const idArchivo = `${props.iphId}-${tipo}-${Date.now()}-${Math.random()}`;
    await guardarAdjunto({ id: idArchivo, iphId: props.iphId, anexo: `D-${tipo}-${id}`, file });
    await cargarImagenes(tipo, id);
    error.value = "";
  } catch (exception) {
    console.error("No se pudo guardar la imagen del Anexo D:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar la imagen en el servidor.";
  } finally {
    event.target.value = "";
  }
}
async function eliminarArchivo(id) {
  try {
    await eliminarAdjunto(id);
    await cargarImagenes("arma", armaActual.value.id);
    await cargarImagenes("objeto", objetoActual.value.id);
  } catch (exception) {
    console.error("No se pudo eliminar la imagen:", exception);
    error.value = "No se pudo eliminar la imagen.";
  }
}
async function descargar(id) {
  try {
    const archivo = await obtenerAdjunto(id);
    if (!archivo) throw new Error("Archivo no encontrado.");
    const url = URL.createObjectURL(archivo.blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = archivo.name;
    link.click();
    URL.revokeObjectURL(url);
  } catch (exception) {
    console.error("No se pudo descargar la imagen:", exception);
    error.value = "No se pudo descargar la imagen seleccionada.";
  }
}
onMounted(cargar);
watch(armaAbierta, (visible) => { if (!visible) imagenesArma.value = []; });
watch(objetoAbierto, (visible) => { if (!visible) imagenesObjeto.value = []; });
</script>
