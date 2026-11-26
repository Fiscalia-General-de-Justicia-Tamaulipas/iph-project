import api from "../../../store/api";
import { guardarCaptura, leerCaptura } from "../../../store/capturas";
import {
  entidades,
  instituciones,
  municipiosTamaulipas,
} from "./PoliciasCatalogos";

const CAMPOS_CAPTURA = [
  "nombres",
  "primer_apellido",
  "segundo_apellido",
  "grado_cargo",
  "institucion",
  "institucion_otra",
  "unidad_arribo",
  "entidad_federativa",
  "municipio_adscripcion",
  "no_aplica",
  "arribo_multiple",
  "cantidad_elementos",
];

export function crearFormularioPolicias() {
  return {
    nombres: "",
    primer_apellido: "",
    segundo_apellido: "",
    grado_cargo: "",
    institucion: "",
    institucion_otra: "",
    unidad_arribo: "",
    entidad_federativa: "",
    municipio_adscripcion: "",
    no_aplica: false,
    arribo_multiple: "",
    cantidad_elementos: null,
    registro_relacional_id: "",
  };
}

function normalizar(valor) {
  return String(valor || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase()
    .trim();
}

export function entidadDesdeAdscripcion(adscripcion) {
  const texto = normalizar(adscripcion);
  return [...entidades]
    .sort((a, b) => b.length - a.length)
    .find((entidad) => texto.includes(normalizar(entidad))) || "";
}

export function municipioDesdeAdscripcion(adscripcion, entidad) {
  if (entidad !== "TAMAULIPAS") return "";
  const texto = normalizar(adscripcion);
  return [...municipiosTamaulipas]
    .sort((a, b) => b.length - a.length)
    .find((municipio) => texto.includes(normalizar(municipio))) || "";
}

function normalizarInstitucion(valor) {
  const clave = normalizar(valor);
  return instituciones.find((item) =>
    normalizar(item.value) === clave || normalizar(item.label) === clave,
  )?.value || valor || "";
}

export function formularioDesdeRegistro(registro) {
  const unidad = registro.unidad_arribo || "";
  const noAplica = normalizar(unidad) === "no aplica";
  return {
    ...crearFormularioPolicias(),
    nombres: registro.nombres || registro.nombre || "",
    primer_apellido: registro.primer_apellido || registro.paterno || "",
    segundo_apellido: registro.segundo_apellido || registro.materno || "",
    grado_cargo: registro.grado_cargo || "",
    institucion: normalizarInstitucion(registro.institucion),
    institucion_otra: registro.institucion_otra || "",
    unidad_arribo: noAplica ? "" : unidad,
    no_aplica: noAplica,
    registro_relacional_id: registro.id == null ? "" : String(registro.id),
  };
}

export function combinarRegistroConCaptura(registro, captura, { priorizarRegistro = false } = {}) {
  const formulario = formularioDesdeRegistro(registro);
  if (!captura || typeof captura !== "object" || Array.isArray(captura)) return formulario;

  const camposRelacionales = new Set([
    "nombres",
    "primer_apellido",
    "segundo_apellido",
    "grado_cargo",
    "institucion",
    "institucion_otra",
    "unidad_arribo",
    "no_aplica",
  ]);
  const resultado = { ...formulario };
  for (const campo of CAMPOS_CAPTURA) {
    if (
      Object.prototype.hasOwnProperty.call(captura, campo)
      && !(priorizarRegistro && camposRelacionales.has(campo))
    ) {
      resultado[campo] = captura[campo];
    }
  }
  resultado.registro_relacional_id = registro?.id == null ? "" : String(registro.id);
  if (resultado.no_aplica || normalizar(resultado.unidad_arribo) === "no aplica") {
    resultado.no_aplica = true;
    resultado.unidad_arribo = "";
  }
  return resultado;
}

function esPrimerRespondiente(registro) {
  return registro.es_primer_respondiente === true
    || registro.es_primer_respondiente === 1
    || registro.es_primer_respondiente === "1"
    || String(registro.es_primer_respondiente).toLocaleLowerCase() === "true";
}

function coincideConCaptura(registro, captura) {
  const comparar = [
    [registro.nombres || registro.nombre, captura.nombres],
    [registro.primer_apellido || registro.paterno, captura.primer_apellido],
    [registro.segundo_apellido || registro.materno, captura.segundo_apellido],
  ];
  return comparar.every(([existente, guardado]) =>
    normalizar(existente) === normalizar(guardado),
  );
}

export async function cargarPolicias(iphId) {
  let captura = null;
  let errorCaptura = "";
  try {
    captura = await leerCaptura(iphId, "policias");
  } catch (error) {
    errorCaptura = error.response?.data?.msg
      || `No se pudo cargar la captura JSON de la Sección 2: ${error.message}`;
  }
  if (captura != null && (typeof captura !== "object" || Array.isArray(captura))) {
    errorCaptura = "La captura JSON guardada de la Sección 2 no tiene un formato válido.";
    captura = null;
  }
  let registros = [];
  let listaCargada = true;
  let errorLista = "";

  try {
    const response = await api.get(`/iph/${iphId}/policias/lista`);
    registros = Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    listaCargada = false;
    errorLista = error.response?.data?.msg || `No se pudo cargar la lista de policías: ${error.message}`;
  }

  const tieneCaptura = Boolean(
    captura && typeof captura === "object" && !Array.isArray(captura) && Object.keys(captura).length,
  );
  const principales = registros.filter(esPrimerRespondiente);
  let registro = null;
  let registrosAmbiguos = [];
  let formulario;
  let datosLegacyIncompletos = false;

  if (tieneCaptura) {
    const coincidencias = principales.filter((item) => coincideConCaptura(item, captura));
    if (coincidencias.length === 1) registro = coincidencias[0];
    else if (principales.length === 1) registro = principales[0];
    else if (principales.length > 1) registrosAmbiguos = principales;

    formulario = combinarRegistroConCaptura(registro, captura);
  } else if (principales.length === 1) {
    registro = principales[0];
    formulario = formularioDesdeRegistro(registro);
    datosLegacyIncompletos = true;
  } else {
    formulario = crearFormularioPolicias();
    if (principales.length > 1) {
      registrosAmbiguos = principales;
      datosLegacyIncompletos = true;
    }
  }

  if (registro?.id != null) formulario.registro_relacional_id = String(registro.id);

  return {
    formulario,
    capturaOriginal: tieneCaptura ? captura : null,
    registros,
    registrosAmbiguos,
    registroId: formulario.registro_relacional_id || "",
    listaCargada,
    errorCarga: [errorCaptura, errorLista].filter(Boolean).join(" "),
    datosLegacyIncompletos,
  };
}

export function datosParaCapturaPolicias(formulario) {
  const captura = Object.fromEntries(CAMPOS_CAPTURA.map((campo) => [campo, formulario[campo] ?? ""]));
  captura.unidad_arribo = formulario.no_aplica ? "NO APLICA" : formulario.unidad_arribo || "";
  return captura;
}

export function validarFormularioPolicias(formulario, { capturaGuiada = false } = {}) {
  const obligatorios = [
    ["primer_apellido", "Primer apellido"],
    ["nombres", "Nombre(s)"],
    ["institucion", "Institución"],
    ["entidad_federativa", "Entidad federativa"],
    ["grado_cargo", "Cargo o grado"],
  ];
  const faltantes = obligatorios
    .filter(([campo]) => !String(formulario[campo] || "").trim())
    .map(([, etiqueta]) => etiqueta);
  if (faltantes.length) return `Completa los campos obligatorios: ${faltantes.join(", ")}.`;

  if (!capturaGuiada && formulario.arribo_multiple === "SI") {
    const cantidad = Number(formulario.cantidad_elementos);
    if (!Number.isInteger(cantidad) || cantidad < 2 || cantidad > 999) {
      return "Indica cuántos elementos arribaron (de 2 a 999).";
    }
  }
  return "";
}

export async function guardarPolicias(iphId, formulario, opciones = {}) {
  const {
    registros = [],
    registroId = formulario.registro_relacional_id,
    listaCargada = true,
    crearNuevo = false,
  } = opciones;
  const captura = datosParaCapturaPolicias(formulario);
  const principales = registros.filter(esPrimerRespondiente);
  let id = registroId ? String(registroId) : "";
  let registroGuardado = null;
  let errorRelacional = "";
  let errorCaptura = "";

  if (!listaCargada) {
    errorRelacional = "No se pudo verificar la lista existente; no se creó un registro para evitar duplicados.";
  } else if (!crearNuevo && !id && principales.length === 1) {
    id = String(principales[0].id);
  } else if (!crearNuevo && !id && principales.length > 1) {
    errorRelacional = "Selecciona el registro de primer respondiente que deseas actualizar.";
  }

  if (listaCargada && !errorRelacional) {
    const payload = {
      nombres: formulario.nombres,
      primer_apellido: formulario.primer_apellido,
      segundo_apellido: formulario.segundo_apellido,
      grado_cargo: formulario.grado_cargo,
      institucion: formulario.institucion,
      institucion_otra: formulario.institucion === "otra" ? formulario.institucion_otra : "",
      unidad_arribo: captura.unidad_arribo,
      es_primer_respondiente: 1,
      id_tipo_actor: 5,
    };
    try {
      const response = id && !crearNuevo
        ? await api.put(`/iph/${iphId}/policias/lista/${encodeURIComponent(id)}`, payload)
        : await api.post(`/iph/${iphId}/policias/lista`, payload);
      registroGuardado = response.data;
      id = response.data?.id == null ? id : String(response.data.id);
    } catch (error) {
      errorRelacional = error.response?.data?.msg
        || `No se pudo guardar el registro relacional: ${error.message}`;
    }
  }

  let capturaGuardada = false;
  try {
    await guardarCaptura(iphId, "policias", captura);
    capturaGuardada = true;
  } catch (error) {
    errorCaptura = error.response?.data?.msg
      || `No se pudo guardar la captura completa de la Sección 2: ${error.message}`;
  }

  const guardadoCompleto = !errorRelacional && capturaGuardada;
  let mensaje;
  if (guardadoCompleto) {
    mensaje = "Sección 2 guardada en la captura JSON y en el registro del primer respondiente.";
  } else if (capturaGuardada) {
    mensaje = `La captura JSON de la Sección 2 sí se guardó, pero el registro relacional no: ${errorRelacional}`;
  } else if (!errorRelacional) {
    mensaje = `El registro relacional sí se guardó, pero la captura JSON no: ${errorCaptura}`;
  } else {
    mensaje = `No se completó el guardado. Registro relacional: ${errorRelacional} Captura JSON: ${errorCaptura}`;
  }

  return {
    guardadoCompleto,
    registroGuardado,
    registroId: id,
    capturaGuardada,
    errorRelacional,
    errorCaptura,
    mensaje,
  };
}

export function opcionesRegistrosPolicias(registros) {
  return registros.map((registro) => ({
    value: String(registro.id),
    label: [
      registro.primer_apellido || registro.paterno,
      registro.segundo_apellido || registro.materno,
      registro.nombres || registro.nombre,
      registro.grado_cargo,
    ].filter(Boolean).join(" "),
  }));
}
