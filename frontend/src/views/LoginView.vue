<template>
  <div class="min-h-screen flex items-center justify-center bg-institucional-oscuro">
    <div class="bg-white rounded-lg shadow-xl p-8 w-full max-w-md">
      <h1 class="text-2xl font-bold text-institucional-verde mb-1">Informe Policial Homologado</h1>
      <p class="text-gray-500 mb-6 text-sm">Inicia sesión para continuar</p>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Usuario o correo</label>
          <input
            v-model="usuario"
            type="text"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-institucional-dorado"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
          <input
            v-model="password"
            type="password"
            required
            class="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-institucional-dorado"
          />
        </div>

        <p v-if="error" class="text-red-600 text-sm">{{ error }}</p>

        <button
          type="submit"
          :disabled="cargando"
          class="w-full bg-institucional-verde text-white py-2 rounded-md font-semibold hover:opacity-90 disabled:opacity-50"
        >
          {{ cargando ? "Ingresando..." : "Iniciar sesión" }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../store/auth";

const usuario = ref("");
const password = ref("");
const error = ref("");
const cargando = ref(false);

const auth = useAuthStore();
const router = useRouter();

async function handleLogin() {
  error.value = "";
  cargando.value = true;
  try {
    await auth.login(usuario.value, password.value);
    router.push({ name: "panel" });
  } catch (e) {
    error.value = e.response?.data?.msg || "No se pudo iniciar sesión";
  } finally {
    cargando.value = false;
  }
}
</script>
