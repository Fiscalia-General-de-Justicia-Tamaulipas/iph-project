import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api",
});

// Adjunta el token JWT guardado en localStorage a cada petición
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("iph_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Si el token expira o es inválido, regresa al login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem("iph_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
