<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>

    <form ref="formulario" class="test-module-form" @submit.prevent="guardar">
      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>ANEXO A. DETENCIÓN(ES)</h2><span>Campo obligatorio*</span></header>
        <div class="test-module-form-body">
          <p class="annex-instruction">Llene este Anexo por cada persona detenida.</p>
          <div class="annex-toolbar">
            <label class="annex-field">
              <span>Número de detención (RND)</span>
              <input v-model="form.rnd" maxlength="20" placeholder="Número de detención (RND)" />
            </label>
            <button type="button" class="test-module-secondary" @click="nuevaDetencion">Nueva detención</button>
            <span class="annex-count">Personas detenidas: {{ detenciones.length }}</span>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.1 Fecha y hora de la detención</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Fecha *</span><input v-model="form.fecha" type="date" required /></label>
          <label class="test-module-field"><span>Hora * (24 horas)</span><input v-model="form.hora" type="time" required /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.2 Datos generales de la persona detenida</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-check annex-check"><input v-model="form.sin_datos" type="checkbox" /> No proporcionó datos</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="form.primer_apellido" :disabled="form.sin_datos" placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.segundo_apellido" :disabled="form.sin_datos" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="form.nombres" :disabled="form.sin_datos" placeholder="NOMBRE(S)" /></label>
            <label class="test-module-field test-module-field-wide"><span>Apodo o alias</span><input v-model="form.alias" :disabled="form.sin_datos || form.alias_no_aplica" placeholder="APODO O ALIAS" /></label>
            <label class="test-module-check"><input v-model="form.alias_no_aplica" type="checkbox" /> No aplica alias</label>
            <label class="test-module-field"><span>Nacionalidad</span><select v-model="form.nacionalidad" :disabled="form.sin_datos"><option value="">- - - -</option><option>NACIONAL</option><option>EXTRANJERO</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><input v-model="form.nacionalidad_especifica" :disabled="form.nacionalidad !== 'EXTRANJERO'" placeholder="¿CUÁL?" /></label>
            <label class="test-module-field"><span>Sexo *</span><select v-model="form.sexo" :disabled="form.sin_datos"><option value="">- - - -</option><option>HOMBRE</option><option>MUJER</option><option>NO ESPECIFICADO</option></select></label>
            <label class="test-module-field"><span>Fecha de nacimiento *</span><input v-model="form.fecha_nacimiento" :disabled="form.sin_datos || form.sin_fecha_nacimiento" type="date" /></label>
            <label class="test-module-check"><input v-model="form.sin_fecha_nacimiento" type="checkbox" /> No proporcionó fecha de nacimiento</label>
            <label class="test-module-field"><span>Edad</span><input :value="edadCalculada" readonly placeholder="EDAD" /></label>
            <label class="test-module-field"><span>¿Se identificó con algún documento?</span><select v-model="form.se_identifico" :disabled="form.sin_datos"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>Tipo de documento</span><select v-model="form.documento" :disabled="form.se_identifico !== 'SÍ'"><option value="">- - - -</option><option>INE</option><option>LICENCIA PARA CONDUCIR</option><option>PASAPORTE</option><option>CÉDULA PROFESIONAL</option><option>OTRO</option></select></label>
            <label class="test-module-field"><span>Especifique documento</span><input v-model="form.documento_otro" :disabled="form.documento !== 'OTRO'" placeholder="ESPECIFICAR" /></label>
            <label class="test-module-field test-module-field-wide"><span>No. de identificación</span><input v-model="form.no_identificacion" :disabled="form.se_identifico !== 'SÍ'" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Domicilio de la persona detenida</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field test-module-field-wide"><span>Calle / Tramo carretero</span><input v-model="form.calle" placeholder="CALLE/TRAMO CARRETERO" /></label>
          <label class="test-module-field"><span>No. exterior</span><input v-model="form.no_exterior" placeholder="NO. EXTERIOR" /></label>
          <label class="test-module-field"><span>No. interior</span><input v-model="form.no_interior" placeholder="NO. INTERIOR" /></label>
          <label class="test-module-field"><span>Código postal</span><input v-model="form.codigo_postal" inputmode="numeric" maxlength="5" placeholder="C P" /></label>
          <label class="test-module-field test-module-field-wide"><span>Colonia / Localidad</span><input v-model="form.colonia" placeholder="COLONIA/LOCALIDAD" /></label>
          <label class="test-module-field test-module-field-wide"><span>Municipio / Demarcación territorial</span><select v-model="form.municipio"><option value="">- SELECCIONE -</option><option v-for="municipio in municipios" :key="municipio">{{ municipio }}</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Entidad federativa</span><select v-model="form.entidad"><option value="">- SELECCIONE -</option><option v-for="entidad in entidades" :key="entidad">{{ entidad }}</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Referencias</span><textarea v-model="form.referencias" rows="2" placeholder="REFERENCIAS" /></label>
        </div>
        <div class="test-module-form-body">
          <label class="test-module-field"><span>Describa brevemente a la persona detenida, incluyendo tipo de vestimenta y rasgos visibles (barba, tatuajes, cicatrices, lunares, bigote, etcétera). *</span><textarea v-model="form.descripcion" rows="3" required placeholder="DESCRIPCIÓN DE LA PERSONA DETENIDA" /></label>
          <div class="test-module-grid annex-questions">
            <label class="test-module-field"><span>¿Presenta lesiones visibles?</span><select v-model="form.lesiones"><option value="">- - - -</option><option>SÍ</option><option>NO</option><option>NO SE SABE</option></select></label>
            <label class="test-module-field"><span>¿Manifiesta padecimiento?</span><select v-model="form.padecimiento"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><input v-model="form.cual_padecimiento" :disabled="form.padecimiento !== 'SÍ'" placeholder="¿CUÁL?" /></label>
            <label class="test-module-field"><span>¿Pertenece a algún grupo vulnerable?</span><select v-model="form.grupo_vulnerable"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><input v-model="form.cual_grupo" :disabled="form.grupo_vulnerable !== 'SÍ'" placeholder="¿CUÁL?" /></label>
            <label class="test-module-field"><span>¿Pertenece a algún grupo delictivo?</span><select v-model="form.grupo_delictivo"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><input v-model="form.cual_grupo_delictivo" :disabled="form.grupo_delictivo !== 'SÍ'" placeholder="¿CUÁL?" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.6 Datos del lugar de la detención</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field test-module-field-wide"><span>¿El lugar de la detención es el mismo que el de la intervención? *</span><select v-model="form.mismo_lugar" @change="copiarLugarIntervencion"><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Calle / Tramo carretero</span><input v-model="form.lugar_calle" :disabled="form.mismo_lugar === 'SÍ'" placeholder="CALLE/TRAMO CARRETERO" /></label>
          <label class="test-module-field"><span>No. exterior</span><input v-model="form.lugar_exterior" :disabled="form.mismo_lugar === 'SÍ'" placeholder="NO. EXTERIOR" /></label>
          <label class="test-module-field"><span>No. interior</span><input v-model="form.lugar_interior" :disabled="form.mismo_lugar === 'SÍ'" placeholder="NO. INTERIOR" /></label>
          <label class="test-module-field"><span>Código postal</span><input v-model="form.lugar_cp" :disabled="form.mismo_lugar === 'SÍ'" maxlength="5" placeholder="C P" /></label>
          <label class="test-module-field test-module-field-wide"><span>Colonia / Localidad *</span><input v-model="form.lugar_colonia" :disabled="form.mismo_lugar === 'SÍ'" required placeholder="COLONIA/LOCALIDAD" /></label>
          <label class="test-module-field test-module-field-wide"><span>Municipio / Demarcación territorial *</span><select v-model="form.lugar_municipio" :disabled="form.mismo_lugar === 'SÍ'" required><option value="">- SELECCIONE -</option><option v-for="municipio in municipios" :key="municipio">{{ municipio }}</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Entidad federativa *</span><select v-model="form.lugar_entidad" :disabled="form.mismo_lugar === 'SÍ'" required><option value="">- SELECCIONE -</option><option v-for="entidad in entidades" :key="entidad">{{ entidad }}</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Referencias *</span><textarea v-model="form.lugar_referencias" :disabled="form.mismo_lugar === 'SÍ'" required placeholder="REFERENCIAS" /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.7 Datos del lugar del traslado de la persona detenida</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Lugar de traslado</span><select v-model="form.lugar_traslado"><option value="">- - - -</option><option>MINISTERIO PÚBLICO</option><option>HOSPITAL</option><option>JUZGADO</option><option>OTRO</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>¿Cuál?</span><textarea v-model="form.lugar_traslado_otro" :disabled="form.lugar_traslado !== 'OTRO'" rows="2" placeholder="¿CUÁL?" /></label>
        </div>
        <div class="test-module-form-body">
          <h3 class="annex-subheading">Observaciones relacionadas con la detención</h3>
          <label class="test-module-field"><span>Describa brevemente la ruta y el medio de traslado desde el lugar de la detención hasta la puesta a disposición, así como la razón de posibles demoras.</span><textarea v-model="form.observaciones" rows="3" placeholder="DESCRIBA BREVEMENTE LA RUTA Y EL MEDIO DE TRASLADO DESDE EL LUGAR DE LA DETENCIÓN." /></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.8 Datos del primer respondiente que realizó la detención</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-check annex-check"><input v-model="form.seleccionar_seccion1" type="checkbox" @change="copiarRespondiente" /> Seleccione Primer Respondiente de la Sección 1</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido</span><input v-model="form.respondiente_primer_apellido" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.respondiente_segundo_apellido" /></label>
            <label class="test-module-field"><span>Nombre(s)</span><input v-model="form.respondiente_nombres" /></label>
            <label class="test-module-field"><span>Adscripción</span><input v-model="form.respondiente_adscripcion" /></label>
            <label class="test-module-field"><span>Cargo / Grado</span><input v-model="form.respondiente_cargo" /></label>
            <label class="test-module-check"><input v-model="form.respondiente_firma" type="checkbox" /> Firma</label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado A.9 Imágenes del detenido</h2></header>
        <div class="test-module-form-body">
          <p class="annex-instruction">Primero debe “Guardar Anexo”; después podrá cargar imágenes JPG, JPEG o BMP de hasta 50 MB.</p>
          <div class="annex-upload">
            <input ref="archivoInput" type="file" accept=".jpg,.jpeg,.bmp,image/jpeg,image/bmp" :disabled="!anexoGuardado" @change="cargarImagen" />
            <button type="button" class="test-module-secondary" :disabled="!anexoGuardado || cargandoImagen" @click="archivoInput?.click()">{{ cargandoImagen ? "Cargando..." : "Cargar archivo" }}</button>
          </div>
          <ul v-if="imagenes.length" class="annex-file-list"><li v-for="imagen in imagenes" :key="imagen.id"><span>{{ imagen.name }}</span><button type="button" class="test-module-remove" @click="descargarImagen(imagen.id)">Descargar</button><button type="button" class="test-module-remove" @click="eliminarImagen(imagen.id)">Eliminar</button></li></ul>
        </div>
      </section>

      <section v-if="detenciones.length" class="test-module-section">
        <header class="test-module-section-heading"><h2>Detenciones capturadas <span>{{ detenciones.length }}</span></h2></header>
        <div class="test-module-table-wrap"><table class="test-module-table"><thead><tr><th>Persona detenida</th><th>RND</th><th>Fecha y hora</th><th>Eliminar</th></tr></thead><tbody><tr v-for="(item, index) in detenciones" :key="item.id"><td>{{ item.nombres }} {{ item.primer_apellido }} {{ item.segundo_apellido }}</td><td>{{ item.rnd || "—" }}</td><td>{{ item.fecha }} {{ item.hora }}</td><td><button type="button" class="test-module-remove" @click="eliminarDetencion(index)">Eliminar</button></td></tr></tbody></table></div>
      </section>

      <div class="test-module-actions test-module-footer">
        <button type="submit" class="test-module-primary" :disabled="guardando">{{ guardando ? "Guardando..." : "Guardar anexo" }}</button>
        <button type="button" class="test-module-next" aria-label="Guardar e ir al siguiente anexo" @click="guardarYSiguiente">➜</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";
import { eliminarAdjunto, guardarAdjunto, listarAdjuntos, obtenerAdjunto } from "../../store/attachments";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "siguiente"]);
const formulario = ref(null);
const entidades = [
  "AGUASCALIENTES", "BAJA CALIFORNIA", "BAJA CALIFORNIA SUR", "CAMPECHE", "CHIAPAS", "CHIHUAHUA",
  "CIUDAD DE MÉXICO", "COAHUILA", "COLIMA", "DURANGO", "GUANAJUATO", "GUERRERO", "HIDALGO", "JALISCO",
  "MÉXICO", "MICHOACÁN", "MORELOS", "NAYARIT", "NUEVO LEÓN", "OAXACA", "PUEBLA", "QUERÉTARO",
  "QUINTANA ROO", "SAN LUIS POTOSÍ", "SINALOA", "SONORA", "TABASCO", "TAMAULIPAS", "TLAXCALA",
  "VERACRUZ", "YUCATÁN", "ZACATECAS",
];
const municipios = [
  "ABASOLO", "ALDAMA", "ALTAMIRA", "ANTIGUO MORELOS", "BURGOS", "BUSTAMANTE", "CAMARGO", "CASAS",
  "CIUDAD MADERO", "CRUILLAS", "GÓMEZ FARÍAS", "GONZÁLEZ", "GÜÉMEZ", "GUERRERO", "GUSTAVO DÍAZ ORDAZ",
  "HIDALGO", "JAUMAVE", "JIMÉNEZ", "LLERA", "MAINERO", "EL MANTE", "MATAMOROS", "MÉNDEZ", "MIER",
  "MIGUEL ALEMÁN", "MIQUIHUANA", "NUEVO LAREDO", "NUEVO MORELOS", "OCAMPO", "PADILLA", "PALMILLAS",
  "REYNOSA", "RÍO BRAVO", "SAN CARLOS", "SAN FERNANDO", "SAN NICOLÁS", "SOTO LA MARINA", "TAMPICO",
  "TULA", "VALLE HERMOSO", "VICTORIA", "VILLAGRÁN", "XICOTÉNCATL",
];
const error = ref("");
const mensaje = ref("");
const guardando = ref(false);
const anexoGuardado = ref(false);
const cargandoImagen = ref(false);
const archivoInput = ref(null);
const imagenes = ref([]);
const detenciones = ref([]);
const form = ref(crearFormulario());

function crearFormulario() {
  return {
    rnd: "", fecha: "", hora: "", sin_datos: false, primer_apellido: "", segundo_apellido: "", nombres: "",
    alias: "", alias_no_aplica: false, nacionalidad: "", nacionalidad_especifica: "", sexo: "",
    fecha_nacimiento: "", sin_fecha_nacimiento: false, se_identifico: "", documento: "", documento_otro: "",
    no_identificacion: "", calle: "", no_exterior: "", no_interior: "", codigo_postal: "", colonia: "",
    municipio: "", entidad: "", referencias: "", descripcion: "", lesiones: "", padecimiento: "",
    cual_padecimiento: "", grupo_vulnerable: "", cual_grupo: "", grupo_delictivo: "",
    cual_grupo_delictivo: "", mismo_lugar: "", lugar_calle: "", lugar_exterior: "", lugar_interior: "",
    lugar_cp: "", lugar_colonia: "", lugar_municipio: "", lugar_entidad: "", lugar_referencias: "",
    lugar_traslado: "", lugar_traslado_otro: "", observaciones: "", seleccionar_seccion1: false,
    respondiente_primer_apellido: "", respondiente_segundo_apellido: "", respondiente_nombres: "",
    respondiente_adscripcion: "", respondiente_cargo: "", respondiente_firma: false,
  };
}

const edadCalculada = computed(() => {
  if (!form.value.fecha_nacimiento) return "";
  const nacimiento = new Date(`${form.value.fecha_nacimiento}T00:00:00`);
  const hoy = new Date();
  let edad = hoy.getFullYear() - nacimiento.getFullYear();
  if (hoy.getMonth() < nacimiento.getMonth() || (hoy.getMonth() === nacimiento.getMonth() && hoy.getDate() < nacimiento.getDate())) edad--;
  return edad >= 0 ? edad : "";
});

async function cargarGuardados() {
  try {
    const saved = await leerCaptura(props.iphId, "anexo_a", `iph-anexo-a:${props.iphId}`) || {};
    if (saved.form) form.value = { ...crearFormulario(), ...saved.form };
    detenciones.value = Array.isArray(saved.detenciones) ? saved.detenciones : [];
    anexoGuardado.value = Boolean(saved.anexoGuardado);
    imagenes.value = await listarAdjuntos(props.iphId, "A");
  } catch (exception) {
    console.error("No se pudieron leer los datos del Anexo A:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron leer los datos guardados del Anexo A en el servidor.";
  }
}

async function persistir() {
  await guardarCaptura(props.iphId, "anexo_a", {
    form: form.value, detenciones: detenciones.value, anexoGuardado: anexoGuardado.value,
  });
}

async function guardar() {
  guardando.value = true;
  error.value = "";
  mensaje.value = "";
  try {
    anexoGuardado.value = true;
    await persistir();
    mensaje.value = "Anexo A guardado en el servidor.";
    emit("guardado");
  } catch (exception) {
    console.error("No se pudo guardar el Anexo A:", exception);
    error.value = exception.response?.data?.msg || "No fue posible guardar el Anexo A en el servidor.";
  } finally {
    guardando.value = false;
  }
}

async function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  await guardar();
  if (!error.value) emit("siguiente");
}

async function nuevaDetencion() {
  if (!form.value.fecha || !form.value.hora || !form.value.descripcion) {
    error.value = "Capture fecha, hora y descripción para agregar una detención.";
    return;
  }
  detenciones.value.push({ ...form.value, id: `${Date.now()}-${Math.random()}` });
  form.value = crearFormulario();
  anexoGuardado.value = false;
  try { await persistir(); } catch (exception) { error.value = exception.response?.data?.msg || "No se pudo guardar la detención en el servidor."; return; }
  mensaje.value = "Detención agregada. Complete los datos de la siguiente persona o guarde el anexo.";
}

async function eliminarDetencion(index) {
  detenciones.value.splice(index, 1);
  try { await persistir(); } catch (exception) { error.value = exception.response?.data?.msg || "No se pudo guardar el cambio en el servidor."; }
}

async function copiarRespondiente() {
  error.value = "";
  if (!form.value.seleccionar_seccion1) return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/policias/lista`);
    const persona = data.find((item) => item.es_primer_respondiente) || data[0];
    if (!persona) throw new Error("No hay primer respondiente capturado en la Sección 1.");
    form.value.respondiente_primer_apellido = persona.primer_apellido || persona.paterno || "";
    form.value.respondiente_segundo_apellido = persona.segundo_apellido || persona.materno || "";
    form.value.respondiente_nombres = persona.nombres || persona.nombre || "";
    form.value.respondiente_adscripcion = persona.institucion_otra || persona.institucion || "";
    form.value.respondiente_cargo = persona.grado_cargo || "";
    form.value.respondiente_firma = true;
  } catch (exception) {
    console.error("No se pudo seleccionar al primer respondiente de la Sección 1:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente de la Sección 1.";
    form.value.seleccionar_seccion1 = false;
  }
}

async function copiarLugarIntervencion() {
  error.value = "";
  if (form.value.mismo_lugar !== "SÍ") return;
  try {
    const { data } = await api.get(`/iph/${props.iphId}/inspeccion_lugar`);
    if (!data) throw new Error("No hay datos del lugar de intervención para copiar.");
    form.value.lugar_calle = data.calle || "";
    form.value.lugar_exterior = data.no_exterior || "";
    form.value.lugar_interior = data.no_interior || "";
    form.value.lugar_colonia = data.colonia || data.localidad || "";
    form.value.lugar_municipio = data.municipio || "";
    form.value.lugar_entidad = data.entidad_federativa || "";
    form.value.lugar_referencias = data.referencias || "";
  } catch (exception) {
    console.error("No se pudieron copiar los datos del lugar de intervención:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudieron copiar los datos del lugar de intervención.";
    form.value.mismo_lugar = "";
  }
}

async function cargarImagen(event) {
  error.value = "";
  const archivo = event.target.files?.[0];
  if (!archivo) return;
  if (!/\.(jpe?g|bmp)$/i.test(archivo.name) || archivo.size > 50 * 1024 * 1024) {
    error.value = "Seleccione una imagen JPG, JPEG o BMP de hasta 50 MB.";
    event.target.value = "";
    return;
  }
  cargandoImagen.value = true;
  try {
    const id = `${props.iphId}-A-${Date.now()}-${Math.random()}`;
    await guardarAdjunto({ id, iphId: props.iphId, anexo: "A", file: archivo });
    imagenes.value = await listarAdjuntos(props.iphId, "A");
  } catch (exception) {
    console.error("No se pudo guardar el archivo del Anexo A:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar el archivo del Anexo A en el servidor.";
  } finally {
    cargandoImagen.value = false;
    event.target.value = "";
  }
}

async function eliminarImagen(id) {
  try {
    await eliminarAdjunto(id);
    imagenes.value = await listarAdjuntos(props.iphId, "A");
  } catch (exception) {
    console.error("No se pudo eliminar el archivo del Anexo A:", exception);
    error.value = "No se pudo eliminar el archivo.";
  }
}

async function descargarImagen(id) {
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
    console.error("No se pudo descargar el archivo del Anexo A:", exception);
    error.value = "No se pudo descargar el archivo seleccionado.";
  }
}

onMounted(cargarGuardados);
</script>
