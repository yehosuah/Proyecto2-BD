<template>
  <div class="auth-grid">
    <article class="card-surface">
      <h1>Iniciar sesion</h1>
      <p class="muted-copy">Clientes y administradores usan el mismo acceso.</p>
      <form class="form-grid" @submit.prevent="submit">
        <label class="form-field">
          <span>Email</span>
          <input v-model="form.email" class="field" required />
        </label>
        <label class="form-field">
          <span>Password</span>
          <input v-model="form.password" class="field" type="password" required />
        </label>
        <p v-if="error" class="error-banner full-width">{{ error }}</p>
        <div class="hero-copy__actions full-width">
          <button class="button button--accent">Entrar</button>
          <RouterLink class="button button--ghost" to="/account/register">Crear cuenta</RouterLink>
        </div>
      </form>
    </article>

    <aside class="card-surface">
      <h2>Credenciales de prueba</h2>
      <div class="demo-creds">
        <p><strong>Admin:</strong> admin@proyecto3.local / admin123</p>
        <p><strong>Inventario:</strong> inventario@proyecto3.local / inventario123</p>
        <p><strong>Ventas:</strong> ventas@proyecto3.local / ventas123</p>
        <p><strong>Reportes:</strong> reportes@proyecto3.local / reportes123</p>
        <p><strong>Cliente:</strong> cliente@proyecto3.local / cliente123</p>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";

import { getBackofficeHomePath } from "../../lib/roles";
import { loginUser } from "../../stores/session";

const route = useRoute();
const router = useRouter();
const error = ref("");
const form = reactive({ email: "admin@proyecto3.local", password: "admin123" });

async function submit() {
  try {
    const user = await loginUser(form);
    const redirect = route.query.redirect || getBackofficeHomePath(user.rol) || "/account/profile";
    router.push(redirect);
  } catch (requestError) {
    error.value = requestError.message;
  }
}
</script>
