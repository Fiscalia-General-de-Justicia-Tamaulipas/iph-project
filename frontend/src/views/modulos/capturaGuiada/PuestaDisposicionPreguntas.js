export function fechaHoyLocal() {
  const hoy = new Date();
  const anio = hoy.getFullYear();
  const mes = String(hoy.getMonth() + 1).padStart(2, "0");
  const dia = String(hoy.getDate()).padStart(2, "0");
  return `${anio}-${mes}-${dia}`;
}

export function horaActualLocal() {
  const ahora = new Date();
  const horas = String(ahora.getHours()).padStart(2, "0");
  const minutos = String(ahora.getMinutes()).padStart(2, "0");
  return `${horas}:${minutos}`;
}

export function formatFecha(fecha) {
  if (!fecha) return "";
  const [anio, mes, dia] = fecha.split("-");
  return anio && mes && dia ? `${dia}/${mes}/${anio}` : fecha;
}

export default [
  {
    id: "saludo",
    pregunta: (datos, respuestas, contexto) =>
      `Hola, ${contexto.nombrePolicia}. Vamos a capturar el IPH con folio ${contexto.folio}.`,
    tipo: "saludo",
    campoFormulario: null,
    obligatorio: true,
  },
  {
    id: "fecha_puesta",
    pregunta: (datos, respuestas, contexto) =>
      `Hoy es ${formatFecha(contexto.fechaHoy)}. ¿Es la fecha de la puesta a disposición?`,
    tipo: "fecha",
    campoFormulario: "fecha",
    sugerencia: (datos, respuestas, contexto) => contexto.fechaHoy,
    obligatorio: true,
  },
  {
    id: "hora_puesta",
    pregunta: (datos, respuestas, contexto) =>
      `Son las ${contexto.horaActual}. ¿Es la hora de la puesta a disposición?`,
    tipo: "hora",
    campoFormulario: "hora",
    sugerencia: (datos, respuestas, contexto) => contexto.horaActual,
    obligatorio: true,
  },
  {
    id: "numero_expediente",
    pregunta: "¿Tienes número de expediente?",
    tipo: "si_no",
    campoFormulario: "no_expediente",
  },
  {
    id: "numero_expediente_texto",
    pregunta: "Escribe el número de expediente.",
    tipo: "texto",
    campoFormulario: "no_expediente",
    obligatorio: false,
    mostrarSi: (datos, respuestas) =>
      respuestas.numero_expediente === "SI" ||
      (!Object.prototype.hasOwnProperty.call(respuestas, "numero_expediente") &&
        Boolean(datos.no_expediente)),
  },
  {
    id: "responsable_sesion",
    pregunta: "¿Eres tú quien realiza la puesta a disposición?",
    tipo: "si_no",
    campoFormulario: "responsable_sesion",
  },
  {
    id: "responsable_primer_apellido",
    pregunta: "Escribe el primer apellido.",
    tipo: "texto",
    campoFormulario: "responsable.primer_apellido",
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.responsable_sesion === "NO",
  },
  {
    id: "responsable_segundo_apellido",
    pregunta: "Escribe el segundo apellido.",
    tipo: "texto",
    campoFormulario: "responsable.segundo_apellido",
    obligatorio: false,
    mostrarSi: (datos, respuestas) => respuestas.responsable_sesion === "NO",
  },
  {
    id: "responsable_nombres",
    pregunta: "Escribe el nombre o los nombres.",
    tipo: "texto",
    campoFormulario: "responsable.nombres",
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.responsable_sesion === "NO",
  },
  {
    id: "responsable_adscripcion",
    pregunta: "Escribe la adscripción.",
    tipo: "texto",
    campoFormulario: "responsable.adscripcion",
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.responsable_sesion === "NO",
  },
  {
    id: "responsable_cargo",
    pregunta: "Escribe el cargo o grado.",
    tipo: "texto",
    campoFormulario: "responsable.cargo",
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.responsable_sesion === "NO",
  },
  {
    id: "responsable_firma",
    pregunta: "¿Se firmará la puesta a disposición?",
    tipo: "si_no",
    campoFormulario: "responsable.firma",
    obligatorio: true,
  },
  {
    id: "resumen",
    pregunta: "Revisión final de los datos capturados.",
    tipo: "resumen",
  },
];
