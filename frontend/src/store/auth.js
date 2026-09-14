import { defineStore } from "pinia";
import api from "./api";

function normalizarUsuario(usuario) {
  if (!usuario || typeof usuario !== "object") return usuario;

  const payload = { ...usuario };
  payload.id_municipio = payload.id_municipio ?? payload.IdMunicipio ?? payload.ID_MNCPIO ?? null;
  payload.id_unidad = payload.id_unidad ?? payload.IdUnidad ?? payload.ID_UNDD ?? null;
  payload.IdMunicipio = payload.IdMunicipio ?? payload.id_municipio ?? null;
  payload.IdUnidad = payload.IdUnidad ?? payload.id_unidad ?? null;
  payload.undd_dscrpcion = payload.undd_dscrpcion ?? payload.UNDD_DSCRPCION ?? payload.adscripcion ?? "";
  payload.UNDD_DSCRPCION = payload.UNDD_DSCRPCION ?? payload.undd_dscrpcion ?? payload.adscripcion ?? "";
  payload.adscripcion = payload.adscripcion ?? payload.UNDD_DSCRPCION ?? payload.undd_dscrpcion ?? "";
  payload.puesto = payload.puesto ?? payload.PUESTO ?? payload.cargo ?? "";
  payload.PUESTO = payload.PUESTO ?? payload.puesto ?? payload.cargo ?? "";
  payload.nombre_completo = payload.nombre_completo ?? payload.nombre ?? payload.usuario ?? "";
  return payload;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    usuario: normalizarUsuario(JSON.parse(localStorage.getItem("iph_usuario") || "null")),
    token: localStorage.getItem("iph_token") || null,
  }),

  getters: {
    estaAutenticado: (state) => !!state.token,
  },

  actions: {
    persistirUsuario(usuario) {
      const normalizado = normalizarUsuario(usuario);
      this.usuario = normalizado;
      localStorage.setItem("iph_usuario", JSON.stringify(normalizado));
      return normalizado;
    },

    async login(usuario, password) {
      const { data } = await api.post("/auth/login", { usuario, password });
      this.token = data.access_token;
      localStorage.setItem("iph_token", data.access_token);
      this.persistirUsuario(data.usuario);
    },

    async sincronizarUsuario() {
      if (!this.token) return null;
      try {
        const { data } = await api.get("/auth/perfil");
        if (data && (data.id_municipio || data.IdMunicipio || data.id_unidad || data.IdUnidad)) {
          this.persistirUsuario(data);
          return this.usuario;
        }
      } catch (error) {
        console.warn("No se pudo refrescar la sesión del usuario:", error);
      }
      return this.usuario;
    },

    cerrarSesion() {
      this.token = null;
      this.usuario = null;
      localStorage.removeItem("iph_token");
      localStorage.removeItem("iph_usuario");
    },
  },
});
