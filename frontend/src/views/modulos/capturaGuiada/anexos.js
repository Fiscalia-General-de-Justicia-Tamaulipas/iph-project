export const anexos = Object.freeze([
  {
    clave: "A",
    nombre: "Anexo A. Detención(es)",
    captura: "anexo_a",
    claveLocal: "iph-anexo-a:{id}",
  },
  {
    clave: "B",
    nombre: "Anexo B. Informe del uso de la fuerza",
    captura: "anexo_b",
    claveLocal: "iph-anexo-b:{id}",
  },
  {
    clave: "C",
    nombre: "Anexo C. Inspección de vehículo",
    captura: "anexo_c_complemento",
    claveLocal: "iph-anexo-c:{id}",
    recursoApi: "inspeccion_vehiculo/lista",
  },
  {
    clave: "D",
    nombre: "Anexo D. Inventario de armas y objetos",
    captura: "anexo_d",
    claveLocal: "iph-anexo-d:{id}",
  },
  {
    clave: "E",
    nombre: "Anexo E. Entrevistas",
    captura: "anexo_e",
    claveLocal: "iph-anexo-e:{id}",
  },
  {
    clave: "F",
    nombre: "Anexo F. Entrega-recepción del lugar de intervención",
    captura: "anexo_f",
    claveLocal: "iph-anexo-f:{id}",
  },
  {
    clave: "G",
    nombre: "Anexo G. Continuación de narrativa",
    captura: "seccion_5_complemento",
    claveLocal: "iph-pruebas:{id}:seccion-5",
    recursoApi: "narracion_primer_respondiente",
  },
].map((anexo) => Object.freeze(anexo)));
