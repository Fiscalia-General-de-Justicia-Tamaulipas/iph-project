import api from "./api";

// IndexedDB se conserva únicamente para migrar adjuntos capturados por versiones previas.
const DATABASE_NAME = "iph-project-files";
const STORE_NAME = "attachments";

function abrirBase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, 1);
    request.onupgradeneeded = () => request.result.createObjectStore(STORE_NAME, { keyPath: "id" });
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("No se pudo abrir el almacenamiento local de archivos."));
  });
}

async function listarLocales(iphId, anexo) {
  const db = await abrirBase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(STORE_NAME).objectStore(STORE_NAME).getAll();
    request.onsuccess = () => {
      db.close();
      resolve(request.result.filter((file) => file.iphId === String(iphId) && file.anexo === anexo));
    };
    request.onerror = () => { db.close(); reject(request.error || new Error("No se pudieron leer los archivos locales.")); };
  });
}

async function borrarLocal(id) {
  const db = await abrirBase();
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    transaction.objectStore(STORE_NAME).delete(id);
    transaction.oncomplete = () => { db.close(); resolve(); };
    transaction.onerror = () => { db.close(); reject(transaction.error || new Error("No se pudo eliminar el archivo local.")); };
  });
}

export async function guardarAdjunto({ id, iphId, anexo, file }) {
  const body = new FormData();
  body.append("id", id);
  body.append("anexo", anexo);
  body.append("file", file, file.name);
  const { data } = await api.post(`/iph/${iphId}/adjuntos`, body);
  return data;
}

export async function listarAdjuntos(iphId, anexo) {
  // Migra al servidor archivos de IndexedDB creados antes de habilitar persistencia remota.
  const antiguos = await listarLocales(iphId, anexo);
  for (const archivo of antiguos) {
    await guardarAdjunto({ id: archivo.id, iphId, anexo, file: new File([archivo.blob], archivo.name, { type: archivo.type }) });
    await borrarLocal(archivo.id);
  }
  const { data } = await api.get(`/iph/${iphId}/adjuntos`, { params: { anexo } });
  return data;
}

export async function obtenerAdjunto(id, iphId) {
  // El id contiene el iphId generado por los formularios actuales. Para IDs históricos
  // el llamador pasa explícitamente el folio.
  const resolvedIphId = iphId ?? String(id).split("-")[0];
  const response = await api.get(`/iph/${resolvedIphId}/adjuntos/${encodeURIComponent(id)}`, { responseType: "blob" });
  const name = response.headers["content-disposition"]?.match(/filename\*=UTF-8''([^;]+)|filename="?([^";]+)"?/i);
  return { id, name: decodeURIComponent(name?.[1] || name?.[2] || "adjunto"), blob: response.data };
}

export async function eliminarAdjunto(id, iphId) {
  const resolvedIphId = iphId ?? String(id).split("-")[0];
  await api.delete(`/iph/${resolvedIphId}/adjuntos/${encodeURIComponent(id)}`);
}
