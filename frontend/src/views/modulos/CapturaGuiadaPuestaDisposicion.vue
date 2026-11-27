<template>
  <CapturaGuiadaMotor
    :preguntas="preguntas"
    :datos="datos"
    :contexto="contexto"
    :inicio-pregunta-id="iniciarEnAnexos ? 'anexo_a' : ''"
    titulo="Puesta a disposición y primer respondiente"
    :resumen-items="resumenItems"
    :resumen-aviso="resumenAviso"
    :resumen-aviso-accion="resumenAvisoAccion"
    :guardando="guardando"
    :error-guardado="errorGuardado || errorGuardadoExterno"
    @actualizar="actualizarCampo"
    @guardar="guardar"
    @accion-secundaria="manejarAccionSecundaria"
    @revisar-formulario="revisarFormularioCompleto"
    @receptor="manejarAvisoResumen"
  />
</template>

<script setup>
import { computed, ref } from "vue";
import CapturaGuiadaMotor from "../../components/CapturaGuiadaMotor.vue";
import { useAuthStore } from "../../store/auth";
import preguntasSeccion, {
  fechaHoyLocal,
  horaActualLocal,
  formatFecha,
} from "./capturaGuiada/PuestaDisposicionPreguntas";
import { anexos } from "./capturaGuiada/anexos.js";
import preguntasPolicias from "./capturaGuiada/PoliciasPreguntas";
import { instituciones } from "./capturaGuiada/PoliciasCatalogos";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  iph: { type: Object, default: null },
  form: { type: Object, required: true },
  formPolicias: { type: Object, required: true },
  contextoPolicias: { type: Object, default: () => ({}) },
  guardarCompleto: { type: Function, required: true },
  iniciarEnAnexos: { type: Boolean, default: false },
  respuestasAnexos: { type: Object, required: true },
  confirmarCambioAnexo: { type: Function, required: true },
  errorGuardadoExterno: { type: String, default: "" },
});

const emit = defineEmits([
  "guardar",
  "actualizar-anexo",
  "actualizar-policia",
  "ningun-anexo",
  "revisar-formulario",
  "revisar-seccion2",
  "receptor",
]);

const auth = useAuthStore();
const guardando = ref(false);
const errorGuardado = ref("");
const form = props.form;

function prefijarPregunta(pregunta) {
  const prefijada = { ...pregunta };
  if (prefijada.campoFormulario) prefijada.campoFormulario = `policias.${prefijada.campoFormulario}`;
  if (prefijada.limpiarCampos) {
    prefijada.limpiarCampos = prefijada.limpiarCampos.map((ruta) => `policias.${ruta}`);
  }
  if (prefijada.alResponder) {
    const alResponder = prefijada.alResponder;
    prefijada.alResponder = async (...argumentos) => {
      const cambios = await alResponder(...argumentos);
      return Object.fromEntries(Object.entries(cambios || {}).map(([ruta, valor]) => [
        `policias.${ruta}`,
        valor,
      ]));
    };
  }
  if (prefijada.accionSecundaria?.actualizar) {
    prefijada.accionSecundaria = {
      ...prefijada.accionSecundaria,
      actualizar: Object.fromEntries(
        Object.entries(prefijada.accionSecundaria.actualizar).map(([ruta, valor]) => [
          `policias.${ruta}`,
          valor,
        ]),
      ),
    };
  }
  return prefijada;
}

const preguntas = [
  ...preguntasSeccion.slice(0, -1),
  {
    id: "inicio_anexos",
    pregunta: "Ahora vamos con los anexos.",
    tipo: "continuar",
  },
  ...anexos.map((anexo, index) => ({
    id: `anexo_${anexo.clave.toLowerCase()}`,
    pregunta: `${anexo.nombre}: ¿se entrega este anexo?`,
    tipo: "si_no",
    campoFormulario: `anexos.${anexo.clave}.entregado`,
    respuestaInicial: (datos) => datos.anexos?.[anexo.clave]?.entregado,
    progreso: {
      actual: index + 1,
      total: anexos.length,
      etiqueta: `Anexo ${index + 1} de ${anexos.length}`,
    },
    confirmarCambio: (valor, datos, respuestas, contexto) =>
      contexto.confirmarCambioAnexo(anexo.clave, valor),
    accionSecundaria: {
      etiqueta: "Ningún anexo",
      respuesta: "Ningún anexo",
      destino: "transicion_seccion2",
      evento: "ningun-anexo",
      confirmar: async (datos, respuestas, contexto) => {
        for (const { clave } of anexos) {
          if (!(await contexto.confirmarCambioAnexo(clave, "NO"))) return false;
        }
        return true;
      },
    },
  })),
  {
    id: "transicion_seccion2",
    pregunta: "Terminamos la Sección 1. Sigue la Sección 2: Primer respondiente.",
    tipo: "continuar",
  },
  ...preguntasPolicias.slice(0, -1).map(prefijarPregunta),
  preguntasPolicias[preguntasPolicias.length - 1],
];

const datos = computed(() => ({
  ...form,
  ...props.formPolicias,
  policias: props.formPolicias,
  anexos: Object.fromEntries(anexos.map(({ clave }) => [
    clave,
    {
      entregado: props.respuestasAnexos[clave] === true
        ? "SI"
        : props.respuestasAnexos[clave] === false
          ? "NO"
          : "",
    },
  ])),
}));

function primerNombreCompleto(nombreCompleto) {
  return String(nombreCompleto || "").trim().split(/\s+/)[0] || "";
}

const nombresSesion = computed(() => {
  const usuario = auth.usuario || {};
  const nombres = String(usuario.NMBRE || usuario.nmbre || "").trim();
  if (nombres) return nombres;
  return primerNombreCompleto(usuario.nombre_completo);
});

const primerApellidoSesion = computed(() =>
  String(auth.usuario?.PTRNO || auth.usuario?.ptrno || "").trim(),
);

const segundoApellidoSesion = computed(() =>
  String(auth.usuario?.MTRNO || auth.usuario?.mtrno || "").trim(),
);

const adscripcionSesion = computed(() =>
  String(auth.usuario?.UNDD_DSCRPCION || auth.usuario?.adscripcion || "").trim(),
);

const cargoSesion = computed(() =>
  String(auth.usuario?.PUESTO || auth.usuario?.puesto || auth.usuario?.cargo || "").trim(),
);

const nombrePolicia = computed(() => {
  const partes = [nombresSesion.value, primerApellidoSesion.value, segundoApellidoSesion.value].filter(Boolean);
  return partes.join(" ") || String(auth.usuario?.usuario || "Usuario");
});

const contexto = computed(() => ({
  nombrePolicia: nombrePolicia.value,
  folio: props.iph?.folio_interno || props.iph?.IPH || props.iph?.folio || props.iphId,
  fechaHoy: fechaHoyLocal(),
  horaActual: horaActualLocal(),
  confirmarCambioAnexo: props.confirmarCambioAnexo,
  nombres: nombresSesion.value,
  primerApellido: primerApellidoSesion.value,
  segundoApellido: segundoApellidoSesion.value,
  adscripcion: adscripcionSesion.value,
  cargo: cargoSesion.value,
  ...props.contextoPolicias,
}));

const resumenItems = computed(() => {
  const entregados = anexos.filter(({ clave }) => props.respuestasAnexos[clave] === true);
  return [
    { etiqueta: "Fecha", valor: formatFecha(form.fecha) || "Sin capturar" },
    { etiqueta: "Hora", valor: form.hora || "Sin capturar" },
    { etiqueta: "Número de expediente", valor: form.no_expediente || "No aplica" },
    { etiqueta: "Primer apellido", valor: form.responsable.primer_apellido || "Sin capturar" },
    { etiqueta: "Segundo apellido", valor: form.responsable.segundo_apellido || "No aplica" },
    { etiqueta: "Nombre(s)", valor: form.responsable.nombres || "Sin capturar" },
    { etiqueta: "Adscripción", valor: form.responsable.adscripcion || "Sin capturar" },
    { etiqueta: "Cargo/Grado", valor: form.responsable.cargo || "Sin capturar" },
    { etiqueta: "Firma", valor: form.responsable.firma === "SI" ? "Sí" : form.responsable.firma === "NO" ? "No" : "Sin capturar" },
    { etiqueta: "Anexos entregados", valor: `${entregados.length} de ${anexos.length}` },
    { etiqueta: "Cuáles", valor: entregados.map(({ nombre }) => nombre).join(", ") || "Ninguno" },
    { etiqueta: "Sección 2 · Primer apellido", valor: props.formPolicias.primer_apellido || "Sin capturar" },
    { etiqueta: "Sección 2 · Segundo apellido", valor: props.formPolicias.segundo_apellido || "No aplica" },
    { etiqueta: "Sección 2 · Nombre(s)", valor: props.formPolicias.nombres || "Sin capturar" },
    {
      etiqueta: "Sección 2 · Institución",
      valor: props.formPolicias.institucion
        ? instituciones.find((item) => item.value === props.formPolicias.institucion)?.label || props.formPolicias.institucion
        : "Sin capturar",
    },
    { etiqueta: "Sección 2 · Entidad federativa", valor: props.formPolicias.entidad_federativa || "Sin capturar" },
    { etiqueta: "Sección 2 · Municipio de adscripción", valor: props.formPolicias.municipio_adscripcion || "No aplica" },
    {
      etiqueta: "Sección 2 · Otra autoridad",
      valor: props.formPolicias.institucion === "otra"
        ? props.formPolicias.institucion_otra || "Sin capturar"
        : "No aplica",
    },
    { etiqueta: "Sección 2 · Cargo o grado", valor: props.formPolicias.grado_cargo || "Sin capturar" },
    {
      etiqueta: "Sección 2 · Unidad de arribo",
      valor: props.formPolicias.no_aplica
        ? "No aplica"
        : props.formPolicias.unidad_arribo || "Sin capturar",
    },
    {
      etiqueta: "Sección 2 · Más de un elemento",
      valor: props.formPolicias.arribo_multiple === "SI"
        ? "Sí"
        : props.formPolicias.arribo_multiple === "NO"
          ? "No"
          : "Sin capturar",
    },
    {
      etiqueta: "Sección 2 · Cantidad de elementos",
      valor: props.formPolicias.arribo_multiple === "SI"
        ? props.formPolicias.cantidad_elementos || "Pendiente en formulario completo"
        : "No aplica",
    },
  ];
});

const faltanDatosPolicias = computed(() =>
  (props.formPolicias.arribo_multiple === "SI"
    && (!Number.isInteger(Number(props.formPolicias.cantidad_elementos))
      || Number(props.formPolicias.cantidad_elementos) < 2
      || Number(props.formPolicias.cantidad_elementos) > 999)),
);
const resumenAviso = computed(() => {
  const avisos = [];
  if (!form.receptor.nombres || !form.receptor.primer_apellido) {
    avisos.push("Falta capturar los datos de quien recibe la puesta a disposición.");
  }
  if (props.contextoPolicias.datosLegacyIncompletos) {
    avisos.push("Este IPH no tenía guardados entidad, municipio ni datos de arribo; verifica y guarda esas respuestas.");
  }
  if (
    props.formPolicias.arribo_multiple === "SI"
    && (!Number.isInteger(Number(props.formPolicias.cantidad_elementos))
      || Number(props.formPolicias.cantidad_elementos) < 2
      || Number(props.formPolicias.cantidad_elementos) > 999)
  ) {
    avisos.push("Falta indicar cuántos elementos arribaron (de 2 a 999) en el formulario completo.");
  }
  return avisos.join(" ");
});
const resumenAvisoAccion = computed(() => {
  if (
    props.formPolicias.arribo_multiple === "SI"
    && (!Number.isInteger(Number(props.formPolicias.cantidad_elementos))
      || Number(props.formPolicias.cantidad_elementos) < 2
      || Number(props.formPolicias.cantidad_elementos) > 999)
  ) return "Abrir formulario completo";
  if (!form.receptor.nombres || !form.receptor.primer_apellido) return "Capturar receptor";
  return "";
});

function establecerRuta(ruta, valor) {
  const partes = ruta.split(".");
  if (partes.length === 1) {
    form[partes[0]] = valor;
    return;
  }
  let actual = form;
  for (let index = 0; index < partes.length - 1; index += 1) {
    if (!actual[partes[index]]) actual[partes[index]] = {};
    actual = actual[partes[index]];
  }
  actual[partes[partes.length - 1]] = valor;
}

function actualizarCampo({ ruta, valor }) {
  const campoPolicia = ruta.match(/^policias\.(.+)$/);
  if (campoPolicia) {
    emit("actualizar-policia", { ruta: campoPolicia[1], valor });
    return;
  }
  const coincideAnexo = ruta.match(/^anexos\.([A-G])\.entregado$/);
  if (coincideAnexo) {
    emit("actualizar-anexo", { clave: coincideAnexo[1], respuesta: valor });
    return;
  }
  establecerRuta(ruta, valor);
}

function manejarAccionSecundaria(accion) {
  if (accion.evento === "ningun-anexo") emit("ningun-anexo");
}

function validarObligatorios() {
  if (!form.fecha) return "Captura la fecha de puesta a disposición.";
  if (!form.hora) return "Captura la hora de puesta a disposición.";
  if (!form.responsable.primer_apellido) return "Captura el primer apellido.";
  if (!form.responsable.nombres) return "Captura el nombre.";
  if (!form.responsable.adscripcion) return "Captura la adscripción.";
  if (!form.responsable.cargo) return "Captura el cargo o grado.";
  if (!["SI", "NO"].includes(form.responsable.firma)) return "Indica si se firmará la puesta.";
  return "";
}

async function guardar() {
  const error = validarObligatorios();
  if (error) {
    errorGuardado.value = error;
    return;
  }

  guardando.value = true;
  errorGuardado.value = "";
  try {
    await props.guardarCompleto();
  } catch (error) {
    errorGuardado.value = error.response?.data?.msg || error.message
      || "No se pudo guardar la Sección 1 y la Sección 2.";
  } finally {
    guardando.value = false;
  }
}

function revisarFormularioCompleto() {
  emit("revisar-seccion2");
}

function manejarAvisoResumen() {
  if (faltanDatosPolicias.value) {
    emit("revisar-seccion2");
    return;
  }
  emit("receptor");
}
</script>
