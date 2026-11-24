<template>
  <CapturaGuiadaMotor
    :preguntas="preguntas"
    :datos="form"
    :contexto="contexto"
    titulo="Puesta a disposición"
    :resumen-items="resumenItems"
    :guardando="guardando"
    :error-guardado="errorGuardado || errorGuardadoExterno"
    @actualizar="actualizarCampo"
    @guardar="guardar"
    @revisar-formulario="revisarFormularioCompleto"
    @receptor="irAReceptor"
  />
</template>

<script setup>
import { computed, ref } from "vue";
import CapturaGuiadaMotor from "../../components/CapturaGuiadaMotor.vue";
import { useAuthStore } from "../../store/auth";
import preguntas, {
  fechaHoyLocal,
  horaActualLocal,
  formatFecha,
} from "./capturaGuiada/PuestaDisposicionPreguntas";

const props = defineProps({
  iphId: { type: [String, Number], required: true },
  iph: { type: Object, default: null },
  form: { type: Object, required: true },
  errorGuardadoExterno: { type: String, default: "" },
});

const emit = defineEmits(["guardar", "revisar-formulario", "receptor"]);

const auth = useAuthStore();
const guardando = ref(false);
const errorGuardado = ref("");
const form = props.form;

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
  nombres: nombresSesion.value,
  primerApellido: primerApellidoSesion.value,
  segundoApellido: segundoApellidoSesion.value,
  adscripcion: adscripcionSesion.value,
  cargo: cargoSesion.value,
}));

const resumenItems = computed(() => [
  { etiqueta: "Fecha", valor: formatFecha(form.fecha) || "Sin capturar" },
  { etiqueta: "Hora", valor: form.hora || "Sin capturar" },
  { etiqueta: "Número de expediente", valor: form.no_expediente || "No aplica" },
  { etiqueta: "Primer apellido", valor: form.responsable.primer_apellido || "Sin capturar" },
  { etiqueta: "Segundo apellido", valor: form.responsable.segundo_apellido || "No aplica" },
  { etiqueta: "Nombre(s)", valor: form.responsable.nombres || "Sin capturar" },
  { etiqueta: "Adscripción", valor: form.responsable.adscripcion || "Sin capturar" },
  { etiqueta: "Cargo/Grado", valor: form.responsable.cargo || "Sin capturar" },
  { etiqueta: "Firma", valor: form.responsable.firma === "SI" ? "Sí" : form.responsable.firma === "NO" ? "No" : "Sin capturar" },
]);

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
  establecerRuta(ruta, valor);
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
