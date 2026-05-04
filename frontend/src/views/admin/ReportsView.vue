<template>
  <div class="surface-stack page-stack">
    <section class="card-surface filters-row">
      <div>
        <h1>Reportes</h1>
        <p class="muted-copy">Ventas por fecha, top productos y alertas de stock.</p>
      </div>
      <div class="filters-row__controls">
        <input v-model="filters.start_date" class="field" type="date" />
        <input v-model="filters.end_date" class="field" type="date" />
        <button class="button button--accent" @click="loadReports">Filtrar</button>
        <a class="button button--ghost" :href="csvUrl" target="_blank" rel="noreferrer">Exportar CSV</a>
      </div>
    </section>

    <section class="admin-grid">
      <article class="card-surface admin-chart">
        <div class="card-header"><h2>Ventas por fecha</h2></div>
        <div class="sparkline sparkline--wide">
          <span v-for="point in sales.series" :key="point.fecha" :style="{ height: `${Math.max(18, point.ventas_totales / 60)}px` }"></span>
        </div>
        <table class="data-table">
          <thead><tr><th>Fecha</th><th>Ordenes</th><th>Ventas</th></tr></thead>
          <tbody>
            <tr v-for="point in sales.series" :key="point.fecha">
              <td>{{ point.fecha }}</td>
              <td>{{ point.ordenes }}</td>
              <td>{{ money(point.ventas_totales) }}</td>
            </tr>
          </tbody>
        </table>
      </article>

      <article class="card-surface">
        <div class="card-header"><h2>Top productos</h2></div>
        <div class="mini-cart">
          <div v-for="item in topProducts" :key="item.sku" class="mini-cart__row">
            <span>{{ item.nombre }}</span>
            <strong>{{ item.vendidos }}</strong>
          </div>
        </div>
      </article>

      <article class="card-surface">
        <div class="card-header"><h2>Stock bajo</h2></div>
        <div class="mini-cart">
          <div v-for="item in lowStock" :key="item.sku" class="mini-cart__row">
            <span>{{ item.nombre }}</span>
            <strong>{{ item.stock_actual }}</strong>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";

import { apiFileUrl, apiRequest } from "../../lib/api";

const sales = reactive({ series: [], summary: null });
const topProducts = ref([]);
const lowStock = ref([]);
const filters = reactive({ start_date: "", end_date: "" });

const csvUrl = computed(() =>
  apiFileUrl("/api/admin/reports/sales/export.csv", {
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  }),
);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

async function loadReports() {
  const params = {
    start_date: filters.start_date || undefined,
    end_date: filters.end_date || undefined,
  };
  const [salesPayload, topPayload, lowPayload] = await Promise.all([
    apiRequest("/api/admin/reports/sales", { params }),
    apiRequest("/api/admin/reports/top-products"),
    apiRequest("/api/admin/reports/low-stock"),
  ]);
  sales.series = salesPayload.series;
  sales.summary = salesPayload.summary;
  topProducts.value = topPayload.items;
  lowStock.value = lowPayload.items;
}

onMounted(loadReports);
</script>

