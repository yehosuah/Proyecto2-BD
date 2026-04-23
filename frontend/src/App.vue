<template>
  <div class="app-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Proyecto 2</p>
        <h1>Storefront + Admin foundation</h1>
        <p class="lede">
          Vue route scaffold for public shopping, client account flows, and admin back-office
          management.
        </p>
      </div>
      <nav class="top-nav">
        <RouterLink to="/">Inicio</RouterLink>
        <RouterLink to="/catalog">Catalogo</RouterLink>
        <RouterLink to="/checkout">Checkout</RouterLink>
        <RouterLink to="/account/profile">Mi cuenta</RouterLink>
        <RouterLink to="/admin">Admin</RouterLink>
      </nav>
    </header>

    <main class="page-frame">
      <aside class="surface-guide">
        <h2>Superficies</h2>
        <ul>
          <li>Storefront publico</li>
          <li>Cuenta cliente</li>
          <li>Back office admin</li>
        </ul>
      </aside>

      <section class="view-panel">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from "vue-router";
</script>

