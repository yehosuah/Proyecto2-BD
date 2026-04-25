<template>
  <div class="app-shell">
    <header class="hero">
      <div>
        <p class="eyebrow">Proyecto 2</p>
        <h1>Tienda e inventario</h1>
        <p class="lede">
          Aplicacion web para administrar productos, registrar ventas y consultar reportes desde una
          base de datos relacional.
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
        <h2>Secciones</h2>
        <ul>
          <li>Tienda</li>
          <li>Cuenta cliente</li>
          <li>Administracion</li>
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
