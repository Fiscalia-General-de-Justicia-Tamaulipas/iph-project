<template>
  <section class="test-module annex-form">
    <p v-if="error" class="test-module-error" role="alert">{{ error }}</p>
    <div class="bitacora-heading">
      <h2>Bitácora de Comentarios de Registros Devueltos</h2>
    </div>
    <div class="test-module-table-wrap bitacora-table-wrap">
      <table class="test-module-table bitacora-table">
        <thead>
          <tr>
            <th>Versión</th>
            <th>Fecha de Comentario</th>
            <th>Sección/Anexo</th>
            <th>Apartado</th>
            <th>Comentario</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!registros.length"><td colspan="5">No hay registros</td></tr>
          <tr v-for="registro in registros" :key="registro.id">
            <td>{{ registro.version }}</td>
            <td>{{ registro.fecha }}</td>
            <td>{{ registro.seccion }}</td>
            <td>{{ registro.apartado }}</td>
            <td>{{ registro.comentario }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr><td colspan="5"><span class="bitacora-page">1</span><span class="bitacora-total">{{ registros.length ? `1 al ${registros.length}` : "0 al 0" }} de {{ registros.length }} Elementos en 1 Páginas</span></td></tr>
        </tfoot>
      </table>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { guardarCaptura, leerCaptura } from "../../store/capturas";

const props = defineProps({ iphId: { type: [String, Number], required: true } });
const registros = ref([]);
const error = ref("");

onMounted(async () => {
  try {
    const saved = await leerCaptura(props.iphId, "bitacora");
    if (saved) registros.value = Array.isArray(saved.registros) ? saved.registros : [];
    else {
      const key = `iph-bitacora:${props.iphId}`;
      const old = localStorage.getItem(key);
      if (old) {
        const rows = JSON.parse(old);
        if (!Array.isArray(rows)) throw new Error("Formato local de bitácora inválido.");
        await guardarCaptura(props.iphId, "bitacora", { registros: rows });
        localStorage.removeItem(key);
        registros.value = rows;
      }
    }
  } catch (exception) {
    console.error("No se pudo cargar la bitácora de comentarios:", exception);
    error.value = exception.response?.data?.msg || "No se pudo cargar la bitácora desde el servidor.";
  }
});
</script>
