<template>
  <article class="card-surface" v-if="detail">
    <div class="section-header">
      <div>
        <h1>{{ detail.order.codigo_publico }}</h1>
        <p class="muted-copy">{{ detail.order.nombre_cliente }} · {{ detail.order.metodo }}</p>
      </div>
      <StatusPill :value="detail.order.estado_pedido" />
    </div>
    <div class="mini-cart">
      <div v-for="item in detail.items" :key="item.id_detalle_pedido" class="mini-cart__row">
        <span>{{ item.nombre }} x {{ item.cantidad }}</span>
        <strong>{{ money(item.precio_unitario * item.cantidad) }}</strong>
      </div>
    </div>
    <div v-if="canChangeStatus" class="hero-copy__actions">
      <button class="button button--ghost" @click="changeStatus('entregado')">Marcar entregado</button>
      <button class="button button--accent" @click="changeStatus('cancelado')">Cancelar</button>
    </div>
  </article>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { requireRouteAccess } from "../../lib/access";
import { hasRole, SALES_WRITE_ROLES } from "../../lib/roles";
import { sessionState } from "../../stores/session";

import StatusPill from "../../components/StatusPill.vue";
import { apiRequest } from "../../lib/api";

const route = useRoute();
const router = useRouter();
const detail = ref(null);
const canChangeStatus = computed(() => hasRole(sessionState.user?.rol, SALES_WRITE_ROLES));

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

async function loadDetail() {
  detail.value = await apiRequest(`/api/admin/sales/${route.params.codigo}`);
}

async function changeStatus(status) {
  if (!canChangeStatus.value) return;
  await apiRequest(`/api/admin/sales/${route.params.codigo}`, {
    method: "PATCH",
    body: { estado_pedido: status },
  });
  await loadDetail();
}

onMounted(async () => {
  if (!(await requireRouteAccess(route, router))) return;
  await loadDetail();
});
</script>
