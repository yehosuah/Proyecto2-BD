<template>
  <div class="site-shell" :class="`site-shell--${surface}`">
    <template v-if="surface === 'admin'">
      <aside class="admin-sidebar">
        <RouterLink class="admin-sidebar__brand" :to="backofficeHomePath || '/'">Tienda Natura</RouterLink>
        <nav class="admin-sidebar__nav">
          <RouterLink v-for="item in backofficeNavItems" :key="item.to" :to="item.to">{{ item.label }}</RouterLink>
        </nav>
        <RouterLink class="admin-sidebar__store" to="/">Ver tienda</RouterLink>
      </aside>
    </template>

    <div class="site-shell__content">
      <header v-if="surface !== 'admin'" class="store-header">
        <RouterLink class="store-brand" to="/">Tienda</RouterLink>
        <nav class="store-nav">
          <RouterLink to="/catalog">Catalogo</RouterLink>
          <RouterLink to="/checkout">Checkout</RouterLink>
          <RouterLink to="/account/profile">Mi cuenta</RouterLink>
        </nav>
        <div class="store-tools">
          <RouterLink class="store-tools__cart" to="/checkout">Carrito {{ cartState.items.length }}</RouterLink>
          <RouterLink v-if="backofficeHomePath" :to="backofficeHomePath">Admin</RouterLink>
        </div>
      </header>

      <main class="surface-frame">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";

import { getBackofficeHomePath, getBackofficeNavItems } from "./lib/roles";
import { cartState, ensureCartLoaded } from "./stores/cart";
import { ensureSessionLoaded, sessionState } from "./stores/session";

const route = useRoute();
const surface = computed(() => route.meta.surface || "store");
const backofficeHomePath = computed(() => getBackofficeHomePath(sessionState.user?.rol));
const backofficeNavItems = computed(() => getBackofficeNavItems(sessionState.user?.rol));

onMounted(async () => {
  ensureCartLoaded();
  await ensureSessionLoaded();
});
</script>
