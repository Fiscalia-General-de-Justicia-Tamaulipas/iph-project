<template>
  <div class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <p v-if="mensaje" class="test-module-success" role="status">{{ mensaje }}</p>
    <section class="test-module-section">
      <header class="test-module-section-heading"><h2>ANEXO E. ENTREVISTAS</h2><button type="button" class="test-module-primary" @click="nuevaEntrevista">Nueva entrevista</button></header>
      <div class="test-module-form-body">
        <p class="annex-instruction">Llene este Anexo por cada persona entrevistada.</p>
        <p class="annex-count">Personas entrevistadas: {{ entrevistas.length }}</p>
      </div>
      <div class="test-module-table-wrap"><table class="test-module-table">
        <thead><tr><th>Paterno</th><th>Materno</th><th>Nombre</th><th>Edad referida</th><th>Nacionalidad</th><th>Editar</th><th>Eliminar</th></tr></thead>
        <tbody><tr v-if="!entrevistas.length"><td colspan="7">No hay registros</td></tr>
          <tr v-for="persona in entrevistas" :key="persona.id"><td>{{ persona.primer_apellido }}</td><td>{{ persona.segundo_apellido }}</td><td>{{ persona.nombres }}</td><td>{{ persona.edad || "—" }}</td><td>{{ persona.nacionalidad }}</td><td><button class="test-module-remove" type="button" @click="editar(persona.id)">Editar</button></td><td><button class="test-module-remove" type="button" @click="eliminar(persona.id)">Eliminar</button></td></tr>
        </tbody></table></div>
    </section>

    <form ref="formulario" class="test-module-form" @submit.prevent="guardarEntrevista">
      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.1 Fecha y hora del lugar de la entrevista</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>Fecha *</span><input v-model="form.fecha" type="date" required /></label>
          <label class="test-module-field"><span>Hora * (24 horas)</span><input v-model="form.hora" type="time" required /></label>
          <label class="test-module-field"><span>¿Desea reservar sus datos? *</span><select v-model="form.reservar_datos" required><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.2 Datos generales</h2></header>
        <div class="test-module-form-body">
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="form.primer_apellido" :disabled="form.reservar_datos === 'SÍ'" :required="form.reservar_datos !== 'SÍ'" placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.segundo_apellido" :disabled="form.reservar_datos === 'SÍ'" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="form.nombres" :disabled="form.reservar_datos === 'SÍ'" :required="form.reservar_datos !== 'SÍ'" placeholder="NOMBRE(S)" /></label>
          </div>
          <p class="annex-instruction">Indique según corresponda.</p>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Calidad *</span><select v-model="form.calidad" required><option value="">- - - -</option><option>VÍCTIMA U OFENDIDO</option><option>DENUNCIANTE</option><option>TESTIGO</option></select></label>
            <label class="test-module-field"><span>Nacionalidad *</span><select v-model="form.nacionalidad" required><option value="">- - - -</option><option>EXTRANJERA</option><option>MEXICANA</option></select></label>
            <label class="test-module-field"><span>¿Cuál?</span><input v-model="form.nacionalidad_otro" :disabled="form.nacionalidad !== 'EXTRANJERA'" placeholder="¿CUÁL?" /></label>
            <label class="test-module-field"><span>Sexo *</span><select v-model="form.sexo" required><option value="">- - - -</option><option>HOMBRE</option><option>MUJER</option></select></label>
            <label class="test-module-check"><input v-model="form.sin_fecha_nacimiento" type="checkbox" /> No proporcionó fecha de nacimiento</label>
            <label class="test-module-field"><span>Fecha de nacimiento *</span><input v-model="form.fecha_nacimiento" :disabled="form.sin_fecha_nacimiento" type="date" :required="!form.sin_fecha_nacimiento" /></label>
            <label class="test-module-field"><span>Edad referida *</span><input v-model.number="form.edad" type="number" min="0" max="150" required placeholder="EDAD REFERIDA" /></label>
            <label class="test-module-field"><span>¿Se identificó con algún documento? *</span><select v-model="form.se_identifico" required><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
            <label class="test-module-field"><span>Tipo de documento</span><select v-model="form.documento" :disabled="form.se_identifico !== 'SÍ'"><option value="">- - - -</option><option>INE</option><option>LICENCIA PARA CONDUCIR</option><option>PASAPORTE</option><option>CÉDULA PROFESIONAL</option><option>OTRO</option></select></label>
            <label class="test-module-field"><span>Especifique documento</span><input v-model="form.documento_otro" :disabled="form.documento !== 'OTRO'" placeholder="ESPECIFIQUE DOCUMENTO" /></label>
            <label class="test-module-field test-module-field-wide"><span>No. de identificación</span><input v-model="form.no_identificacion" :disabled="form.se_identifico !== 'SÍ'" /></label>
            <label class="test-module-field"><span>No. telefónico</span><input v-model="form.telefono" type="tel" /></label>
            <label class="test-module-field"><span>Correo electrónico</span><input v-model="form.correo" type="email" placeholder="CORREO ELECTRÓNICO" /></label>
          </div>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Domicilio de la persona entrevistada</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field test-module-field-wide"><span>Calle / Tramo carretero</span><input v-model="form.calle" placeholder="CALLE/TRAMO CARRETERO" /></label>
          <label class="test-module-field"><span>No. exterior</span><input v-model="form.no_exterior" placeholder="NO. EXTERIOR" /></label>
          <label class="test-module-field"><span>No. interior</span><input v-model="form.no_interior" placeholder="NO. INTERIOR" /></label>
          <label class="test-module-field"><span>Código postal</span><input v-model="form.codigo_postal" maxlength="5" placeholder="C P" /></label>
          <label class="test-module-field test-module-field-wide"><span>Colonia / Localidad</span><input v-model="form.colonia" placeholder="COLONIA/LOCALIDAD" /></label>
          <label class="test-module-field"><span>Entidad federativa</span><select v-model="form.entidad" @change="form.municipio = ''"><option value="">- SELECCIONE -</option><option v-for="entidad in entidades" :key="entidad">{{ entidad }}</option></select></label>
          <label class="test-module-field"><span>Municipio / Demarcación territorial</span><select v-model="form.municipio"><option value="">- SELECCIONE -</option><option v-if="form.entidad === 'TAMAULIPAS'" value="NO APLICA">NO APLICA</option><option v-for="municipio in municipios" :key="municipio">{{ municipio }}</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>Referencias</span><textarea v-model="form.referencias" rows="2" placeholder="REFERENCIA" /></label>
        </div>
        <p class="annex-pad annex-instruction">Comuníquele al entrevistado la facultad de abstención que le otorga el artículo 361 del Código Nacional de Procedimientos Penales.</p>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.3 Relato de la entrevista</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-field"><textarea v-model="form.relato" rows="5" placeholder="RELATO DE LA ENTREVISTA" /></label>
          <label class="annex-signature">Firma/Huella de la persona entrevistada: * <span><input v-model="form.firma_entrevistado" type="radio" value="SÍ" required /> Sí</span><span><input v-model="form.firma_entrevistado" type="radio" value="NO" /> No</span></label>
        </div>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.4 Datos del lugar del traslado o canalización de la persona entrevistada</h2></header>
        <div class="test-module-grid test-module-form-body">
          <label class="test-module-field"><span>¿Trasladó o canalizó a la persona entrevistada? *</span><select v-model="form.traslado" required><option value="">- - - -</option><option>SÍ</option><option>NO</option></select></label>
          <label class="test-module-field"><span>Lugar de traslado o canalización</span><select v-model="form.lugar_traslado" :disabled="form.traslado !== 'SÍ'"><option value="">- - - -</option><option>MINISTERIO PÚBLICO</option><option>HOSPITAL</option><option>DOMICILIO</option><option>OTRO</option></select></label>
          <label class="test-module-field test-module-field-wide"><span>¿Cuál?</span><textarea v-model="form.lugar_traslado_otro" :disabled="form.traslado !== 'SÍ'" rows="2" placeholder="¿CUÁL?" /></label>
        </div>
      </section>

      <section v-if="form.calidad === 'VÍCTIMA U OFENDIDO'" class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.5 Constancia de lectura de derechos, SÓLO en caso de víctima u ofendido</h2></header>
        <label class="annex-signature">Firma/Huella de la víctima u ofendido: <span><input v-model="form.firma_derechos" type="radio" value="SÍ" /> Sí</span><span><input v-model="form.firma_derechos" type="radio" value="NO" /> No</span></label>
      </section>

      <section class="test-module-section">
        <header class="test-module-section-heading"><h2>Apartado E.6 Datos del primer respondiente que realizó la entrevista, sólo si es diferente a quien firmó la puesta a disposición</h2></header>
        <div class="test-module-form-body">
          <label class="test-module-check annex-check"><input v-model="form.seleccionar_seccion1" type="checkbox" @change="copiarRespondiente" /> Seleccione Primer Respondiente de la Sección 1</label>
          <div class="test-module-grid">
            <label class="test-module-field"><span>Primer apellido *</span><input v-model="form.respondiente_primer_apellido" required placeholder="PRIMER APELLIDO" /></label>
            <label class="test-module-field"><span>Segundo apellido</span><input v-model="form.respondiente_segundo_apellido" placeholder="SEGUNDO APELLIDO" /></label>
            <label class="test-module-field"><span>Nombre(s) *</span><input v-model="form.respondiente_nombres" required placeholder="NOMBRE(S)" /></label>
            <label class="test-module-field"><span>Adscripción *</span><input v-model="form.respondiente_adscripcion" required placeholder="ADSCRIPCIÓN" /></label>
            <label class="test-module-field"><span>Cargo / grado *</span><input v-model="form.respondiente_cargo" required placeholder="CARGO/GRADO" /></label>
            <label class="test-module-check"><input v-model="form.respondiente_firma" type="checkbox" /> Firma/Huella</label>
          </div>
        </div>
      </section>

      <div class="test-module-actions test-module-footer">
        <button type="submit" class="test-module-primary" :disabled="guardando">{{ guardando ? "Guardando..." : "Guardar anexo" }}</button>
        <button type="button" class="test-module-next" aria-label="Guardar e ir al siguiente anexo" @click="guardarYSiguiente">➜</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../../store/api";
import { guardarCaptura, leerCaptura } from "../../store/capturas";

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
const form = ref(crearFormulario());
const entrevistas = ref([]);
const editando = ref("");
const error = ref("");
const mensaje = ref("");
const guardando = ref(false);

function crearFormulario() {
  return {
    fecha: "", hora: "", reservar_datos: "", primer_apellido: "", segundo_apellido: "", nombres: "",
    calidad: "", nacionalidad: "", nacionalidad_otro: "", sexo: "", sin_fecha_nacimiento: false,
    fecha_nacimiento: "", edad: "", se_identifico: "", documento: "", documento_otro: "",
    no_identificacion: "", telefono: "", correo: "", calle: "", no_exterior: "", no_interior: "",
    codigo_postal: "", colonia: "", entidad: "", municipio: "", referencias: "", relato: "",
    firma_entrevistado: "", traslado: "", lugar_traslado: "", lugar_traslado_otro: "", firma_derechos: "",
    seleccionar_seccion1: false, respondiente_primer_apellido: "", respondiente_segundo_apellido: "",
    respondiente_nombres: "", respondiente_adscripcion: "", respondiente_cargo: "", respondiente_firma: false,
  };
}

async function cargar() {
  try {
    const saved = await leerCaptura(props.iphId, "anexo_e", `iph-anexo-e:${props.iphId}`) || {};
    entrevistas.value = Array.isArray(saved.entrevistas) ? saved.entrevistas : [];
  } catch (exception) {
    console.error("No se pudieron cargar las entrevistas del Anexo E:", exception);
    error.value = exception.response?.data?.msg || "No se pudieron leer las entrevistas guardadas en el servidor.";
  }
}

async function persistir() {
  await guardarCaptura(props.iphId, "anexo_e", { entrevistas: entrevistas.value });
}

function nuevaEntrevista() {
  form.value = crearFormulario();
  editando.value = "";
  mensaje.value = "";
  error.value = "";
}

function editar(id) {
  const entrevista = entrevistas.value.find((item) => item.id === id);
  if (!entrevista) return;
  form.value = { ...crearFormulario(), ...entrevista };
  editando.value = id;
  mensaje.value = "";
}

async function guardarEntrevista() {
  guardando.value = true;
  error.value = "";
  try {
    const entrevista = { ...form.value, id: editando.value || `${Date.now()}-${Math.random()}` };
    const index = entrevistas.value.findIndex((item) => item.id === entrevista.id);
    if (index < 0) entrevistas.value.push(entrevista);
    else entrevistas.value[index] = entrevista;
    await persistir();
    form.value = crearFormulario();
    editando.value = "";
    mensaje.value = "Entrevista guardada.";
    emit("guardado");
    return true;
  } catch (exception) {
    console.error("No se pudo guardar la entrevista:", exception);
    error.value = exception.response?.data?.msg || "No se pudo guardar la entrevista en el servidor.";
    return false;
  } finally {
    guardando.value = false;
  }
}

async function guardarYSiguiente() {
  if (!formulario.value?.reportValidity()) return;
  if (await guardarEntrevista()) emit("siguiente");
}

async function eliminar(id) {
  entrevistas.value = entrevistas.value.filter((item) => item.id !== id);
  try {
    await persistir();
    if (editando.value === id) nuevaEntrevista();
  } catch (exception) {
    console.error("No se pudo eliminar la entrevista:", exception);
    error.value = "No se pudo eliminar la entrevista.";
  }
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
    console.error("No se pudo cargar el primer respondiente:", exception);
    error.value = exception.response?.data?.msg || exception.message || "No se pudo cargar el primer respondiente.";
    form.value.seleccionar_seccion1 = false;
  }
}

onMounted(cargar);
</script>
