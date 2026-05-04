<template>
  <div v-if="product" class="product-detail">
    <div class="product-detail__visual card-surface">
      <ProductVisual :product="product" />
    </div>
    <article class="product-detail__content card-surface">
      <p class="section-kicker">{{ product.categoria_nombre }}</p>
      <h1>{{ product.nombre }}</h1>
      <p class="muted-copy">{{ product.descripcion }}</p>
      <dl class="detail-list">
        <div><dt>SKU</dt><dd>{{ product.sku }}</dd></div>
        <div><dt>Proveedor</dt><dd>{{ product.proveedor_nombre || "Sin proveedor" }}</dd></div>
        <div><dt>Stock</dt><dd>{{ product.stock_actual }}</dd></div>
      </dl>
      <strong class="detail-price">{{ money(product.precio_unitario) }}</strong>
      <div class="hero-copy__actions">
        <button class="button button--accent" @click="addToCart(product)">Agregar</button>
        <RouterLink class="button button--ghost" to="/checkout">Ir a checkout</RouterLink>
      </div>
    </article>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import ProductVisual from "../../components/ProductVisual.vue";
import { apiRequest } from "../../lib/api";
import { addToCart } from "../../stores/cart";

const route = useRoute();
const product = ref(null);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

onMounted(async () => {
  product.value = await apiRequest(`/api/catalog/products/${route.params.sku}`);
});
</script>

