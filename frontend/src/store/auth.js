import { defineStore } from "pinia";
import api from "./api";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    usuario: JSON.parse(localStorage.getItem("iph_usuario") || "null"),
    token: localStorage.getItem("iph_token") || null,
  }),

  getters: {
    estaAutenticado: (state) => !!state.token,
  },

  actions: {
    async login(usuario, password) {
      const { data } = await api.post("/auth/login", { usuario, password });
      this.token = data.access_token;
      this.usuario = data.usuario;
      localStorage.setItem("iph_token", data.access_token);
      localStorage.setItem("iph_usuario", JSON.stringify(data.usuario));
    },

    cerrarSesion() {
      this.token = null;
      this.usuario = null;
      localStorage.removeItem("iph_token");
      localStorage.removeItem("iph_usuario");
    },
  },
});
