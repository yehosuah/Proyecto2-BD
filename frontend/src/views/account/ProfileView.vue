<template>
  <article class="card-surface" v-if="sessionState.user">
    <h1>Mi perfil</h1>
    <dl class="detail-list">
      <div><dt>Nombre</dt><dd>{{ sessionState.user.nombre }} {{ sessionState.user.apellido }}</dd></div>
      <div><dt>Email</dt><dd>{{ sessionState.user.email }}</dd></div>
      <div><dt>Telefono</dt><dd>{{ sessionState.user.telefono || "No registrado" }}</dd></div>
      <div><dt>Rol</dt><dd>{{ sessionState.user.rol }}</dd></div>
    </dl>
    <div class="hero-copy__actions">
      <RouterLink class="button button--ghost" to="/account/orders">Ver pedidos</RouterLink>
      <button class="button button--accent" @click="logout">Cerrar sesion</button>
    </div>
  </article>
</template>

<script setup>
import { RouterLink, useRouter } from "vue-router";

import { logoutUser, sessionState } from "../../stores/session";

const router = useRouter();

async function logout() {
  await logoutUser();
  router.push("/");
}
</script>

