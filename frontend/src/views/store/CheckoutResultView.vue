<template>
  <article class="card-surface result-panel" v-if="result">
    <StatusPill :value="result.payment.estado" />
    <h1>Resultado del checkout</h1>
    <p class="muted-copy">Codigo de pedido: {{ result.order.codigo_publico }}</p>
    <div class="result-grid">
      <div>
        <h2>Cliente</h2>
        <p>{{ result.order.nombre_cliente }}</p>
        <p>{{ result.order.email_cliente }}</p>
      </div>
      <div>
        <h2>Pago</h2>
        <p>{{ result.payment.metodo }}</p>
        <p>{{ result.payment.estado }}</p>
      </div>
    </div>
    <div class="mini-cart">
      <div v-for="item in result.items" :key="item.id_detalle_pedido" class="mini-cart__row">
        <span>{{ item.nombre }} x {{ item.cantidad }}</span>
        <strong>{{ money(item.precio_unitario * item.cantidad) }}</strong>
      </div>
    </div>
  </article>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import StatusPill from "../../components/StatusPill.vue";
import { apiRequest } from "../../lib/api";
import { getLastOrder } from "../../stores/cart";
import { ensureSessionLoaded, sessionState } from "../../stores/session";

const route = useRoute();
const result = ref(null);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

onMounted(async () => {
  const cached = getLastOrder();
  if (cached?.order?.codigo_publico === route.params.codigo) {
    result.value = cached;
    return;
  }
  await ensureSessionLoaded();
  if (sessionState.authenticated) {
    result.value = await apiRequest(`/api/orders/${route.params.codigo}`);
  }
});
</script>

