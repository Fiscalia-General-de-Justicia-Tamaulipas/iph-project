<template>
  <div class="min-h-screen flex items-center justify-center bg-[#e8e8e8] px-4 py-10">
    <div class="w-full max-w-5xl overflow-hidden rounded-[28px] border border-[#cfcfcf] bg-white shadow-institucional grid md:grid-cols-[1.2fr_0.8fr]">
      <div class="relative hidden md:flex flex-col justify-between bg-gradient-to-br from-[#575756] via-[#878787] to-[#dadada] p-10 text-white">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.25),transparent_35%)]"></div>
        <div class="relative z-10">
          <img src="/logos/logo_fgjtam.png" alt="Logo FJGTAM" class="h-20 w-auto object-contain mb-6 drop-shadow-lg" />
          <p class="text-xs uppercase tracking-[0.35em] text-white/80">FGJ Tamaulipas</p>
          <h1 class="mt-6 text-4xl font-black leading-tight">Informe Policial</h1>
          <h2 class="text-2xl font-semibold text-white/90">Homologado</h2>
        </div>
        <div class="relative z-10 text-sm text-white/85 leading-relaxed max-w-sm">
          Sistema institucional para la captura, control y seguimiento de la información del IPH.
        </div>
      </div>

      <div class="flex items-center justify-center p-8 md:p-10">
        <div class="w-full max-w-md">
          <div class="mb-8 text-center md:text-left">
            <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" class="mx-auto md:mx-0 h-16 w-auto mb-4" />
            <p class="text-xs font-semibold uppercase tracking-[0.28em] text-[#575756]">Acceso al sistema</p>
            <h2 class="mt-3 text-3xl font-black text-[#1f1f1e]">Iniciar sesión</h2>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-[#575756] mb-2">Usuario o correo</label>
              <input
                v-model="usuario"
                type="text"
                required
                class="w-full rounded-xl border border-[#c8c8c8] bg-[#f7f7f7] px-3 py-3 text-[#1f1f1e] placeholder:text-[#878787] focus:border-[#575756] focus:outline-none focus:ring-2 focus:ring-[#dadada]"
                placeholder="Ingrese su usuario"
              />
            </div>
            <div>
              <label class="block text-sm font-semibold text-[#575756] mb-2">Contraseña</label>
              <input
                v-model="password"
                type="password"
                required
                class="w-full rounded-xl border border-[#c8c8c8] bg-[#f7f7f7] px-3 py-3 text-[#1f1f1e] placeholder:text-[#878787] focus:border-[#575756] focus:outline-none focus:ring-2 focus:ring-[#dadada]"
                placeholder="••••••••"
              />
            </div>

            <p v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{{ error }}</p>

            <button
              type="submit"
              :disabled="cargando"
              class="w-full rounded-xl bg-[#575756] px-4 py-3 text-base font-bold text-white transition hover:bg-[#454545] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {{ cargando ? "Ingresando..." : "Iniciar sesión" }}
            </button>
          </form>
        </div>
      </div>
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
