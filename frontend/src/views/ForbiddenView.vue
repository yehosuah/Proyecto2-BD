<template>
  <article class="card-surface">
    <h1>403 · No autorizado</h1>
    <p class="muted-copy">No tienes permisos para acceder a este recurso.</p>
    <div class="hero-copy__actions">
      <RouterLink class="button button--accent" to="/">Ir al inicio</RouterLink>
    </div>
  </article>
</template>

<script setup>
import { RouterLink } from "vue-router";
</script>
