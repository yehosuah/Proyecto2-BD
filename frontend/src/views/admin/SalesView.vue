<template>
  <article class="card-surface">
    <div class="section-header">
      <div>
        <h1>Ventas</h1>
        <p class="muted-copy">Pedidos creados desde la tienda.</p>
      </div>
      <select v-model="statusFilter" class="field sales-filter" @change="loadSales">
        <option value="">Todos los estados</option>
        <option value="listo_para_retiro">Listo para retiro</option>
        <option value="en_preparacion">En preparacion</option>
        <option value="cancelado">Cancelado</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr><th>Codigo</th><th>Cliente</th><th>Entrega</th><th>Pago</th><th>Estado</th><th>Total</th></tr>
      </thead>
      <tbody>
        <tr v-for="sale in sales" :key="sale.codigo_publico">
          <td><RouterLink :to="`/admin/sales/${sale.codigo_publico}`">{{ sale.codigo_publico }}</RouterLink></td>
          <td>{{ sale.nombre_cliente }}</td>
          <td>{{ sale.tipo_entrega }}</td>
          <td>{{ sale.pago_metodo }}</td>
          <td><StatusPill :value="sale.estado_pedido" /></td>
          <td>{{ money(sale.total_pedido) }}</td>
        </tr>
      </tbody>
    </table>
  </article>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { RouterLink } from "vue-router";

import { requireRouteAccess } from "../../lib/access";

import StatusPill from "../../components/StatusPill.vue";
import { apiRequest } from "../../lib/api";


const route = useRoute();
const router = useRouter();
const sales = ref([]);
const statusFilter = ref("");

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

async function loadSales() {
  const payload = await apiRequest("/api/admin/sales", {
    params: { status_filter: statusFilter.value || undefined },
  });
  sales.value = payload.items;
}

onMounted(async () => {
  if (!(await requireRouteAccess(route, router))) return;
  await loadSales();
});
</script>

