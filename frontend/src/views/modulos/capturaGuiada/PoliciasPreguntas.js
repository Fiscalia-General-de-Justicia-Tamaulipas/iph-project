import {
  entidades,
  instituciones,
  municipiosTamaulipas,
} from "./PoliciasCatalogos";

export default [
  {
    id: "seleccionar_registro_existente",
    pregunta: "Hay varios registros de primer respondiente en este IPH. Selecciona cuál deseas continuar o corregir.",
    tipo: "seleccion_busqueda",
    campoFormulario: "registro_relacional_id",
    opciones: (datos, respuestas, contexto) => contexto.registrosAmbiguos || [],
    mostrarSi: (datos, respuestas, contexto) => (contexto.registrosAmbiguos || []).length > 1,
    obligatorio: true,
  },
  {
    id: "misma_persona_seccion1",
    pregunta: (datos) => {
      const nombreActual = [
        datos.nombres,
        datos.primer_apellido,
        datos.segundo_apellido,
      ].filter(Boolean).join(" ");
      return nombreActual
        ? `Los datos actuales son ${nombreActual}. ¿El primer respondiente es la misma persona que realizó la puesta a disposición?`
        : "¿El primer respondiente es la misma persona que realizó la puesta a disposición?";
    },
    tipo: "si_no",
    obligatorio: true,
    alResponder: async (respuesta, datos, respuestas, contexto) => {
      if (respuesta === "NO") {
        return {
          primer_apellido: "",
          segundo_apellido: "",
          nombres: "",
          grado_cargo: "",
        };
      }

      const responsable = await contexto.leerResponsableSeccion1();
      return {
        primer_apellido: responsable.primer_apellido || "",
        segundo_apellido: responsable.segundo_apellido || "",
        nombres: responsable.nombres || "",
        grado_cargo: responsable.cargo || "",
      };
    },
  },
  {
    id: "primer_apellido",
    pregunta: "Escribe el primer apellido.",
    tipo: "texto",
    campoFormulario: "primer_apellido",
    maxlength: 100,
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.misma_persona_seccion1 === "NO",
  },
  {
    id: "segundo_apellido",
    pregunta: "Escribe el segundo apellido, si aplica.",
    tipo: "texto",
    campoFormulario: "segundo_apellido",
    maxlength: 100,
    mostrarSi: (datos, respuestas) => respuestas.misma_persona_seccion1 === "NO",
  },
  {
    id: "nombres",
    pregunta: "Escribe el nombre o los nombres.",
    tipo: "texto",
    campoFormulario: "nombres",
    maxlength: 150,
    obligatorio: true,
    mostrarSi: (datos, respuestas) => respuestas.misma_persona_seccion1 === "NO",
  },
  {
    id: "institucion",
    pregunta: "Selecciona la institución a la que pertenece.",
    tipo: "seleccion_busqueda",
    campoFormulario: "institucion",
    opciones: instituciones,
    obligatorio: true,
  },
  {
    id: "entidad_adscripcion_sesion",
    pregunta: (datos, respuestas, contexto) =>
      `¿Su entidad de adscripción es ${contexto.entidadSesion}?`,
    tipo: "si_no",
    mostrarSi: (datos, respuestas, contexto) => !datos.entidad_federativa
      && Boolean(contexto.entidadSesion),
    alResponder: (respuesta, datos, respuestas, contexto) =>
      respuesta === "SI" ? { entidad_federativa: contexto.entidadSesion } : {},
  },
  {
    id: "entidad_federativa",
    pregunta: "Selecciona la entidad federativa de adscripción.",
    tipo: "seleccion_busqueda",
    campoFormulario: "entidad_federativa",
    opciones: entidades.map((entidad) => ({ value: entidad, label: entidad })),
    limpiarCampos: ["municipio_adscripcion"],
    limpiarPreguntasDependientes: ["municipio_adscripcion", "municipio_adscripcion_sesion"],
    obligatorio: true,
  },
  {
    id: "municipio_adscripcion_sesion",
    pregunta: (datos, respuestas, contexto) =>
      `¿Su municipio de adscripción es ${contexto.municipioSesion}?`,
    tipo: "si_no",
    mostrarSi: (datos, respuestas, contexto) =>
      datos.entidad_federativa === "TAMAULIPAS"
      && !datos.municipio_adscripcion
      && Boolean(contexto.municipioSesion),
    alResponder: (respuesta, datos, respuestas, contexto) =>
      respuesta === "SI" ? { municipio_adscripcion: contexto.municipioSesion } : {},
  },
  {
    id: "municipio_adscripcion",
    pregunta: "Selecciona el municipio de adscripción.",
    tipo: "seleccion_dependiente",
    campoFormulario: "municipio_adscripcion",
    dependeDe: "entidad_federativa",
    opciones: (datos) => datos.entidad_federativa === "TAMAULIPAS"
      ? municipiosTamaulipas.map((municipio) => ({ value: municipio, label: municipio }))
      : [],
    mostrarSi: (datos) => datos.entidad_federativa === "TAMAULIPAS",
  },
  {
    id: "institucion_otra",
    pregunta: "Escribe el nombre de la otra autoridad.",
    tipo: "texto",
    campoFormulario: "institucion_otra",
    maxlength: 150,
    mostrarSi: (datos) => datos.institucion === "otra",
  },
  {
    id: "grado_cargo",
    pregunta: (datos) => datos.grado_cargo
      ? `¿Su cargo o grado es ${datos.grado_cargo}?`
      : "¿Cuál es su cargo o grado?",
    tipo: "texto",
    campoFormulario: "grado_cargo",
    maxlength: 100,
    obligatorio: true,
    sugerencia: (datos, respuestas, contexto) => datos.grado_cargo
      || (respuestas.misma_persona_seccion1 === "SI" ? contexto.cargoSesion : ""),
  },
  {
    id: "unidad_arribo",
    pregunta: "¿En qué unidad arribó al lugar de la intervención?",
    tipo: "texto",
    campoFormulario: "unidad_arribo",
    maxlength: 100,
    respuestaInicial: (datos) => datos.no_aplica ? "NO APLICA" : datos.unidad_arribo,
    accionSecundaria: {
      etiqueta: "No aplica",
      respuesta: "No aplica",
      actualizar: { unidad_arribo: "NO APLICA", no_aplica: true },
    },
  },
  {
    id: "arribo_multiple",
    pregunta: "¿Arribó más de un elemento al lugar de la intervención?",
    tipo: "si_no",
    campoFormulario: "arribo_multiple",
    respuestaInicial: (datos) => datos.arribo_multiple,
    alResponder: (respuesta) => ({ arribo_multiple: respuesta }),
  },
  {
    id: "resumen",
    pregunta: "Revisa los datos de identificación y adscripción capturados.",
    tipo: "resumen",
  },
];
