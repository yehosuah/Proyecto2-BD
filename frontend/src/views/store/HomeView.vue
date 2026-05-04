<template>
  <div class="surface-stack page-stack">
    <section class="hero-grid">
      <article class="hero-copy">
        <p class="section-kicker">Productos destacados</p>
        <h1>Calidad que transforma tu día a día.</h1>
        <p class="hero-copy__text">
          Productos seleccionados con cuidado para tu hogar, tu estilo y tu bienestar.
        </p>
        <div class="hero-copy__actions">
          <RouterLink class="button button--accent" to="/catalog">Catalogo</RouterLink>
          <RouterLink class="button button--ghost" to="/checkout">Checkout</RouterLink>
        </div>
      </article>

      <article class="hero-stage hero-stage--photo card-surface">
        <img
          src="/assets/product-photos/hero-home-goods.png"
          alt="Seleccion de productos para hogar, cocina, bano y bienestar"
        />
      </article>

      <aside class="cart-aside card-surface">
        <div class="card-header">
          <h2>Tu carrito</h2>
          <span>{{ cartItems.length }} items</span>
        </div>
        <div v-if="cartItems.length" class="mini-cart">
          <div v-for="item in cartItems.slice(0, 3)" :key="item.id_producto" class="mini-cart__row">
            <div>
              <p>{{ item.nombre }}</p>
              <small>Cantidad: {{ item.cantidad }}</small>
            </div>
            <strong>{{ money(item.precio_unitario * item.cantidad) }}</strong>
          </div>
        </div>
        <p v-else class="muted-copy">Agrega productos desde el catalogo para preparar la compra.</p>
        <div class="mini-cart__footer">
          <strong>Total</strong>
          <strong>{{ money(cartTotal) }}</strong>
        </div>
        <RouterLink class="button button--accent button--block" to="/checkout">Ver carrito</RouterLink>
      </aside>
    </section>

    <section class="card-surface section-block">
      <div class="card-header">
        <h2>Categorias</h2>
      </div>
      <div class="category-strip">
        <button
          v-for="category in categories.slice(0, 7)"
          :key="category.id_categoria"
          class="category-pill"
          @click="goToCategory(category.id_categoria)"
        >
          <span>{{ category.nombre }}</span>
        </button>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <h2>Productos destacados</h2>
        <RouterLink class="text-link" to="/catalog">Ver catalogo completo</RouterLink>
      </div>

      <div class="product-grid">
        <article v-for="product in featuredProducts" :key="product.id_producto" class="product-card">
          <ProductVisual :product="product" />
          <div class="product-card__body">
            <RouterLink :to="`/catalog/${product.sku}`" class="product-card__title">
              {{ product.nombre }}
            </RouterLink>
            <p class="muted-copy">{{ product.categoria_nombre }}</p>
            <strong class="product-card__price">{{ money(product.precio_unitario) }}</strong>
          </div>
          <button class="button button--accent button--block" @click="addProduct(product)">Agregar</button>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter, RouterLink } from "vue-router";

import ProductVisual from "../../components/ProductVisual.vue";
import { apiRequest } from "../../lib/api";
import { addToCart, cartState, cartTotal, ensureCartLoaded } from "../../stores/cart";

const router = useRouter();
const categories = ref([]);
const products = ref([]);

const featuredProducts = computed(() => products.value.slice(0, 6));
const cartItems = computed(() => cartState.items);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

function addProduct(product) {
  addToCart(product);
}

function goToCategory(categoryId) {
  router.push({ name: "catalog", query: { category: categoryId } });
}

onMounted(async () => {
  ensureCartLoaded();
  const [categoryPayload, productPayload] = await Promise.all([
    apiRequest("/api/catalog/categories"),
    apiRequest("/api/catalog/products"),
  ]);
  categories.value = categoryPayload.items;
  products.value = productPayload.items;
});
</script>
