<template>
  <CapturaGuiadaMotor
    :preguntas="preguntas"
    :datos="datos"
    :contexto="contexto"
    :inicio-pregunta-id="iniciarEnAnexos ? 'anexo_a' : ''"
    titulo="Puesta a disposición"
    :resumen-items="resumenItems"
    :guardando="guardando"
    :error-guardado="errorGuardado || errorGuardadoExterno"
    @actualizar="actualizarCampo"
    @guardar="guardar"
    @accion-secundaria="manejarAccionSecundaria"
    @revisar-formulario="revisarFormularioCompleto"
    @receptor="irAReceptor"
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

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  iph: { type: Object, default: null },
  form: { type: Object, required: true },
  iniciarEnAnexos: { type: Boolean, default: false },
  respuestasAnexos: { type: Object, required: true },
  confirmarCambioAnexo: { type: Function, required: true },
  errorGuardadoExterno: { type: String, default: "" },
});

const emit = defineEmits([
  "guardar",
  "actualizar-anexo",
  "ningun-anexo",
  "revisar-formulario",
  "receptor",
]);

const auth = useAuthStore();
const guardando = ref(false);
const errorGuardado = ref("");
const form = props.form;

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
      destino: "resumen",
      evento: "ningun-anexo",
      confirmar: async (datos, respuestas, contexto) => {
        for (const { clave } of anexos) {
          if (!(await contexto.confirmarCambioAnexo(clave, "NO"))) return false;
        }
        return true;
      },
    },
  })),
  preguntasSeccion[preguntasSeccion.length - 1],
];

const datos = computed(() => ({
  ...form,
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
  ];
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
  emit("guardar");
  guardando.value = false;
}

function revisarFormularioCompleto() {
  emit("revisar-formulario");
}

function irAReceptor() {
  emit("receptor");
}
</script>
