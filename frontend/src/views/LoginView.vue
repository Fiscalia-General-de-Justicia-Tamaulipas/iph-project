<template>
  <div class="login-page">
    <div class="login-scene">
      <div class="scene-orb orb-one"></div>
      <div class="scene-orb orb-two"></div>
      <div class="scene-grid"></div>

      <header class="login-header">
        <div class="brand-mini">
          <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" />
        </div>
        <span class="brand-tag">FGJ Tamaulipas</span>
      </header>

      <div class="login-grid">
        <section class="identity-panel">
          <div class="identity-badge">Sistema institucional</div>
          <h1>Informe Policial<br />Homologado</h1>
          <p>
            Centraliza la captura, validación y seguimiento de los registros del IPH con una experiencia de trabajo institucional, segura y profesional.
          </p>

          <div class="identity-stack">
            <div class="mini-stat">
              <span class="mini-label">Expediente</span>
              <strong>IPH</strong>
            </div>
            <div class="mini-stat">
              <span class="mini-label">Seguimiento</span>
              <strong>En línea</strong>
            </div>
            <div class="mini-stat">
              <span class="mini-label">Acceso</span>
              <strong>Autorizado</strong>
            </div>
          </div>
        </section>

        <section class="auth-panel">
          <div class="auth-card">
            <div class="auth-title-row">
              <div class="auth-mark">
                <img src="/logos/logo_fgjtam.png" alt="Logo FGJTAM" />
              </div>
              <div>
                <p class="auth-kicker">Acceso</p>
                <h2>Iniciar sesión</h2>
              </div>
            </div>

            <form @submit.prevent="handleLogin" class="login-form">
              <div class="field-group">
                <label for="usuario">Usuario</label>
                <input id="usuario" v-model="usuario" type="text" required placeholder="Ingrese su usuario" />
              </div>

              <div class="field-group">
                <label for="password">Contraseña</label>
                <input id="password" v-model="password" type="password" required placeholder="••••••••" />
              </div>

              <p v-if="error" class="error-message">{{ error }}</p>

              <button type="submit" :disabled="cargando" class="submit-btn">
                {{ cargando ? "Ingresando..." : "Iniciar sesión" }}
              </button>
            </form>
          </div>
        </section>
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
