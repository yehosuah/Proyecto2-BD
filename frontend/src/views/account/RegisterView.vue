<template>
  <article class="card-surface">
    <h1>Crear cuenta</h1>
    <form class="form-grid" @submit.prevent="submit">
      <label class="form-field"><span>Nombre</span><input v-model="form.nombre" class="field" required /></label>
      <label class="form-field"><span>Apellido</span><input v-model="form.apellido" class="field" required /></label>
      <label class="form-field"><span>Email</span><input v-model="form.email" class="field" required /></label>
      <label class="form-field"><span>Telefono</span><input v-model="form.telefono" class="field" /></label>
      <label class="form-field full-width"><span>Password</span><input v-model="form.password" class="field" type="password" required /></label>
      <p v-if="error" class="error-banner full-width">{{ error }}</p>
      <div class="hero-copy__actions full-width">
        <button class="button button--accent">Crear cuenta</button>
      </div>
    </form>
  </article>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";

import { registerUser } from "../../stores/session";

const router = useRouter();
const error = ref("");
const form = reactive({
  nombre: "",
  apellido: "",
  email: "",
  telefono: "",
  password: "",
});

async function submit() {
  try {
    await registerUser(form);
    router.push("/account/profile");
  } catch (requestError) {
    error.value = requestError.message;
  }
}
</script>

