<template>
  <div class="admin-grid">
    <section class="card-surface admin-chart">
      <div class="section-header">
        <div>
          <h1>Ventas</h1>
          <p class="muted-copy">Resumen operativo del periodo.</p>
        </div>
        <RouterLink class="button button--ghost" to="/admin/reports">Reportes</RouterLink>
      </div>
      <div class="metric-row">
        <div class="metric-box">
          <span>Total ventas</span>
          <strong>{{ money(snapshot.summary?.ventas_totales || 0) }}</strong>
        </div>
        <div class="metric-box">
          <span>Ordenes</span>
          <strong>{{ snapshot.summary?.total_ordenes || 0 }}</strong>
        </div>
      </div>
      <div class="sparkline">
        <span v-for="point in snapshot.sales.slice(-10)" :key="point.fecha" :style="{ height: `${Math.max(18, point.ventas_totales / 60)}px` }"></span>
      </div>
    </section>

    <section class="card-surface">
      <div class="card-header">
        <h2>Top productos</h2>
      </div>
      <div class="mini-cart">
        <div v-for="item in snapshot.top_products" :key="item.nombre" class="mini-cart__row">
          <span>{{ item.nombre }}</span>
          <strong>{{ item.vendidos }}</strong>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { RouterLink } from "vue-router";

import { requireRouteAccess } from "../../lib/access";

import { apiRequest } from "../../lib/api";


const route = useRoute();
const router = useRouter();
const snapshot = reactive({
  sales: [],
  top_products: [],
  summary: null,
});

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

onMounted(async () => {
  if (!(await requireRouteAccess(route, router))) return;
  const [reportPayload, snapshotPayload] = await Promise.all([
    apiRequest("/api/admin/reports/sales"),
    apiRequest("/api/reporting/snapshot"),
  ]);
  snapshot.sales = reportPayload.series;
  snapshot.summary = reportPayload.summary;
  snapshot.top_products = snapshotPayload.top_products;
});
</script>

