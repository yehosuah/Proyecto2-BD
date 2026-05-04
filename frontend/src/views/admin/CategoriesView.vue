<template>
  <div class="admin-two-column">
    <article class="card-surface">
      <h1>Categorias</h1>
      <form class="form-grid" @submit.prevent="saveCategory">
        <label class="form-field"><span>Nombre</span><input v-model="form.nombre" class="field" required /></label>
        <label class="form-field full-width"><span>Descripcion</span><textarea v-model="form.descripcion" class="field field--textarea"></textarea></label>
        <div class="hero-copy__actions full-width">
          <button class="button button--accent">{{ editingId ? "Actualizar" : "Crear" }}</button>
          <button class="button button--ghost" type="button" @click="resetForm">Limpiar</button>
        </div>
      </form>
    </article>

    <article class="card-surface">
      <table class="data-table">
        <thead><tr><th>Nombre</th><th></th></tr></thead>
        <tbody>
          <tr v-for="category in categories" :key="category.id_categoria">
            <td>{{ category.nombre }}</td>
            <td class="table-actions">
              <button class="text-button" @click="editCategory(category)">Editar</button>
              <button class="text-button text-button--danger" @click="removeCategory(category.id_categoria)">Eliminar</button>
            </td>
          </tr>
        </tbody>
      </table>
    </article>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import { apiRequest } from "../../lib/api";

const categories = ref([]);
const editingId = ref(null);
const form = reactive({ nombre: "", descripcion: "", activa: true });

function resetForm() {
  editingId.value = null;
  Object.assign(form, { nombre: "", descripcion: "", activa: true });
}

async function loadCategories() {
  const payload = await apiRequest("/api/admin/categories");
  categories.value = payload.items;
}

function editCategory(category) {
  editingId.value = category.id_categoria;
  Object.assign(form, category);
}

async function saveCategory() {
  if (editingId.value) {
    await apiRequest(`/api/admin/categories/${editingId.value}`, { method: "PUT", body: form });
  } else {
    await apiRequest("/api/admin/categories", { method: "POST", body: form });
  }
  await loadCategories();
  resetForm();
}

async function removeCategory(categoryId) {
  await apiRequest(`/api/admin/categories/${categoryId}`, { method: "DELETE" });
  await loadCategories();
}

onMounted(loadCategories);
</script>

