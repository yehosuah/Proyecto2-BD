<template>
  <article class="card-surface">
    <div class="section-header">
      <div>
        <h1>Historial de pedidos</h1>
        <p class="muted-copy">Solo aparecen pedidos vinculados a tu cuenta.</p>
      </div>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>Codigo</th>
          <th>Entrega</th>
          <th>Estado</th>
          <th>Total</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.codigo_publico">
          <td><RouterLink :to="`/account/orders/${order.codigo_publico}`">{{ order.codigo_publico }}</RouterLink></td>
          <td>{{ order.tipo_entrega }}</td>
          <td><StatusPill :value="order.estado_pedido" /></td>
          <td>{{ money(order.total_pedido) }}</td>
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
const orders = ref([]);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

onMounted(async () => {
  if (!(await requireRouteAccess(route, router))) return;
  const payload = await apiRequest("/api/orders/me");
  orders.value = payload.items;
});
</script>

