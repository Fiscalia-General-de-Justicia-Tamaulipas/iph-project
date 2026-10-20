<template>
  <div class="conocimiento-form">
    <form @submit.prevent="guardar">
      <h2 class="conocimiento-subheading">Apartado 3.1 Conocimiento del hecho por el primer respondiente</h2>

      <div class="conocimiento-intake-grid">
        <div class="conocimiento-field">
          <label for="conocimiento-medio">¿Cómo se enteró del hecho?</label>
          <select id="conocimiento-medio" v-model="form.como_se_entero">
            <option value="">--SELECCIONE--</option>
            <option value="denuncia">DENUNCIA</option>
            <option value="llamada_emergencia">LLAMADA DE EMERGENCIA</option>
            <option value="flagrancia">FLAGRANCIA</option>
            <option value="descubrimiento">DESCUBRIMIENTO</option>
            <option value="localizacion">LOCALIZACIÓN</option>
            <option value="aportacion">APORTACIÓN</option>
            <option value="mandamiento_judicial">MANDAMIENTO JUDICIAL</option>
          </select>
        </div>

        <div v-if="form.como_se_entero === 'llamada_emergencia'" class="conocimiento-field">
          <label for="conocimiento-911">911 No.</label>
          <input id="conocimiento-911" v-model="form.numero_911" type="text" />
        </div>
      </div>

      <div class="conocimiento-times">
        <div class="conocimiento-time-fields">
          <div class="conocimiento-field">
            <label for="conocimiento-fecha">Fecha de conocimiento</label>
            <input id="conocimiento-fecha" v-model="form.fecha_conocimiento" type="date" />
          </div>
          <div class="conocimiento-field">
            <label for="conocimiento-hora">Hora</label>
            <input id="conocimiento-hora" v-model="form.hora_conocimiento" type="time" />
            <small>(24 horas)</small>
          </div>
        </div>

        <fieldset class="conocimiento-arrival">
          <legend>Arribo al Lugar</legend>
          <div class="conocimiento-field">
            <label for="arribo-fecha">Fecha:</label>
            <input id="arribo-fecha" v-model="form.fecha_arribo" type="date" />
          </div>
          <div class="conocimiento-field">
            <label for="arribo-hora">Hora:</label>
            <input id="arribo-hora" v-model="form.hora_arribo" type="time" />
            <small>(24 horas)</small>
          </div>
        </fieldset>
      </div>

      <div class="conocimiento-actions">
        <button type="submit" :disabled="guardando" class="conocimiento-save">
          {{ guardando ? "GUARDANDO..." : "GUARDAR SECCIÓN" }}
        </button>
        <button
          type="button"
          class="conocimiento-next"
          aria-label="Guardar y continuar a la siguiente sección"
          :disabled="guardando"
          @click="guardarYContinuar"
        >
          <span aria-hidden="true">➜</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../../store/auth";
import api from "../../store/api";

const auth = useAuthStore();
const props = defineProps({ iphId: { type: [String, Number], required: true } });
const emit = defineEmits(["guardado", "cancelar", "siguiente"]);

const form = ref({
  id_institucion_informante: "",
  fecha_conocimiento: "",
  hora_conocimiento: "00:00",
  id_cargo: "",
  id_estado: "28",
  id_municipio: auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? "41",
  como_se_entero: "",
  numero_911: "",
  fecha_arribo: "",
  hora_arribo: "00:00",
});
const guardando = ref(false);

function mapearRegistro(data) {
  if (!data) return;
  form.value = {
    ...form.value,
    id_institucion_informante: data.id_institucion_informante ?? data.ID_INSTITUCION_INFORMANTE ?? data.id_institucion ?? "",
    fecha_conocimiento: data.fecha_conocimiento ?? data.FECHA_CONOCIMIENTO ?? "",
    hora_conocimiento: data.hora_conocimiento ?? data.HORA_CONOCIMIENTO ?? "00:00",
    id_cargo: data.id_cargo ?? data.ID_CARGO ?? "",
    id_estado: data.id_estado ?? data.ID_ESTADO ?? "28",
    id_municipio: data.id_municipio ?? data.ID_MUNICIPIO ?? auth.usuario?.id_municipio ?? auth.usuario?.IdMunicipio ?? "41",
    como_se_entero: data.como_se_entero ?? data.COMO_SE_ENTERO ?? "",
    numero_911: data.numero_911 ?? data.NUMERO_911 ?? "",
    fecha_arribo: data.fecha_arribo ?? data.FECHA_ARRIBO ?? "",
    hora_arribo: data.hora_arribo ?? data.HORA_ARRIBO ?? "00:00",
  };
}

async function cargar() {
  const { data } = await api.get(`/iph/${props.iphId}/conocimiento_hecho`);
  if (data) {
    mapearRegistro(data);
  }
}

async function guardar() {
  guardando.value = true;
  try {
    const payload = {
      ...form.value,
      id_usuario: auth.usuario?.id_usuario ?? auth.usuario?.id ?? null,
      id_estado: form.value.id_estado || 28,
      id_municipio: form.value.id_municipio || auth.usuario?.id_municipio || auth.usuario?.IdMunicipio || 41,
    };
    await api.put(`/iph/${props.iphId}/conocimiento_hecho`, payload);
    emit("guardado");
  } finally {
    guardando.value = false;
  }
}

async function guardarYContinuar() {
  await guardar();
  emit("siguiente");
}

onMounted(cargar);
</script>

<style scoped>
.conocimiento-form {
  width: 100%;
  color: #303030;
  font-family: Arial, sans-serif;
}

.conocimiento-form form {
  display: grid;
  gap: 0.85rem;
}

.conocimiento-subheading {
  margin: 0;
  padding: 0.55rem 0.7rem;
  border: 1px solid #d8d8d8;
  background: #f2f2f2;
  color: #454545;
  font-size: 0.82rem;
  font-weight: 700;
}

.conocimiento-intake-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1rem;
  align-items: end;
  padding: 0 0.7rem 0.55rem;
  border-bottom: 1px solid #dedede;
}

.conocimiento-field {
  display: grid;
  min-width: 0;
  gap: 0.25rem;
}

.conocimiento-field label {
  color: #333;
  font-size: 0.68rem;
}

.conocimiento-field input,
.conocimiento-field select {
  width: 100%;
  min-height: 1.9rem;
  padding: 0.3rem 0.5rem;
  border: 1px solid #cfcfcf;
  border-radius: 3px;
  background: #fff;
  color: #343434;
  font-size: 0.75rem;
}

.conocimiento-field small {
  color: #555;
  font-size: 0.62rem;
}

.conocimiento-times {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1.25rem;
  align-items: center;
  padding: 1rem 0.7rem 0.55rem;
}

.conocimiento-time-fields {
  display: grid;
  gap: 0.6rem;
  padding: 0.5rem;
}

.conocimiento-arrival {
  display: grid;
  gap: 0.55rem;
  margin: 0;
  padding: 0.55rem;
  border: 1px solid #dedede;
  border-radius: 3px;
}

.conocimiento-arrival legend {
  width: 100%;
  padding: 0.35rem;
  border: 1px solid #dedede;
  background: #f2f2f2;
  color: #303030;
  font-size: 0.75rem;
  font-weight: 700;
  text-align: center;
}

.conocimiento-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(2rem, 9vw, 8rem);
  padding: 0.4rem 0 0.2rem;
}

.conocimiento-save {
  min-height: 2rem;
  padding: 0.4rem 0.8rem;
  border: 1px solid #575756;
  border-radius: 3px;
  background: #575756;
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
}

.conocimiento-save:hover:not(:disabled) {
  background: #434342;
}

.conocimiento-next {
  display: grid;
  width: 2rem;
  height: 2rem;
  place-items: center;
  border: 0;
  border-radius: 50%;
  background: #666666;
  color: #fff;
  font-size: 1.2rem;
}

.conocimiento-save:disabled,
.conocimiento-next:disabled {
  cursor: wait;
  opacity: 0.65;
}

@media (max-width: 650px) {
  .conocimiento-intake-grid,
  .conocimiento-times {
    grid-template-columns: minmax(0, 1fr);
  }

  .conocimiento-times {
    gap: 0.5rem;
    padding-top: 0.5rem;
  }

  .conocimiento-actions {
    justify-content: space-around;
    gap: 1rem;
  }
}
</style>
