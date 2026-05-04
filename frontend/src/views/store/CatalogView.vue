<template>
  <div class="surface-stack page-stack">
    <section class="card-surface filters-row">
      <div>
        <h1>Catalogo</h1>
        <p class="muted-copy">Explora productos activos y agregalos al carrito.</p>
      </div>
      <div class="filters-row__controls">
        <input v-model="filters.search" class="field" placeholder="Buscar por nombre o SKU" />
        <select v-model="filters.categoryId" class="field">
          <option value="">Todas las categorias</option>
          <option v-for="category in categories" :key="category.id_categoria" :value="category.id_categoria">
            {{ category.nombre }}
          </option>
        </select>
        <button class="button button--ghost" @click="loadProducts">Filtrar</button>
      </div>
    </section>

    <section class="product-grid">
      <article v-for="product in products" :key="product.id_producto" class="product-card">
        <ProductVisual :product="product" />
        <div class="product-card__body">
          <div class="product-card__meta">
            <span>{{ product.categoria_nombre }}</span>
            <span>Stock: {{ product.stock_actual }}</span>
          </div>
          <RouterLink :to="`/catalog/${product.sku}`" class="product-card__title">
            {{ product.nombre }}
          </RouterLink>
          <p class="muted-copy">{{ product.descripcion }}</p>
          <strong class="product-card__price">{{ money(product.precio_unitario) }}</strong>
        </div>
        <div class="product-card__actions">
          <button class="button button--accent button--block" @click="addProduct(product)">Agregar</button>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import ProductVisual from "../../components/ProductVisual.vue";
import { apiRequest } from "../../lib/api";
import { addToCart, ensureCartLoaded } from "../../stores/cart";

const route = useRoute();
const categories = ref([]);
const products = ref([]);
const filters = reactive({
  search: "",
  categoryId: route.query.category || "",
});

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

async function loadProducts() {
  const payload = await apiRequest("/api/catalog/products", {
    params: {
      search: filters.search || undefined,
      category_id: filters.categoryId || undefined,
    },
  });
  products.value = payload.items;
}

function addProduct(product) {
  addToCart(product);
}

onMounted(async () => {
  ensureCartLoaded();
  const categoryPayload = await apiRequest("/api/catalog/categories");
  categories.value = categoryPayload.items;
  await loadProducts();
});
</script>

