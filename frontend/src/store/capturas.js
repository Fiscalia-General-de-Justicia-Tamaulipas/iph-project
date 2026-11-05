import api from "./api";

export async function leerCaptura(iphId, pantalla, claveLocal = "") {
  const { data } = await api.get(`/iph/${iphId}/capturas/${pantalla}`);
  if (data == null && claveLocal) {
    const local = localStorage.getItem(claveLocal);
    if (local !== null) {
      const antiguos = JSON.parse(local);
      if (!antiguos || typeof antiguos !== "object" || Array.isArray(antiguos)) {
        throw new Error("Los datos locales antiguos no tienen un formato válido.");
      }
      await guardarCaptura(iphId, pantalla, antiguos);
      localStorage.removeItem(claveLocal);
      return antiguos;
    }
  }
  return data;
}

export async function guardarCaptura(iphId, pantalla, datos) {
  const { data } = await api.put(`/iph/${iphId}/capturas/${pantalla}`, datos);
  return data;
}
