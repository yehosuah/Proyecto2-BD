<template>
  <div class="admin-two-column">
    <article class="card-surface">
      <h1>Productos</h1>
      <form class="form-grid" @submit.prevent="saveProduct">
        <label class="form-field"><span>SKU</span><input v-model="form.sku" class="field" required /></label>
        <label class="form-field"><span>Nombre</span><input v-model="form.nombre" class="field" required /></label>
        <label class="form-field"><span>Categoria</span>
          <select v-model.number="form.id_categoria" class="field" required>
            <option v-for="category in categories" :key="category.id_categoria" :value="category.id_categoria">{{ category.nombre }}</option>
          </select>
        </label>
        <label class="form-field"><span>Proveedor ID</span><input v-model.number="form.id_proveedor" class="field" /></label>
        <label class="form-field"><span>Precio</span><input v-model.number="form.precio_unitario" class="field" type="number" step="0.01" /></label>
        <label class="form-field"><span>Stock</span><input v-model.number="form.stock_actual" class="field" type="number" /></label>
        <label class="form-field full-width"><span>Descripcion</span><textarea v-model="form.descripcion" class="field field--textarea"></textarea></label>
        <div class="hero-copy__actions full-width">
          <button class="button button--accent">{{ editingId ? "Actualizar" : "Crear" }}</button>
          <button class="button button--ghost" type="button" @click="resetForm">Limpiar</button>
        </div>
      </form>
    </article>

    <article class="card-surface">
      <div class="card-header"><h2>Listado</h2></div>
      <table class="data-table">
        <thead><tr><th>SKU</th><th>Nombre</th><th>Stock</th><th></th></tr></thead>
        <tbody>
          <tr v-for="product in products" :key="product.id_producto">
            <td>{{ product.sku }}</td>
            <td>{{ product.nombre }}</td>
            <td>{{ product.stock_actual }}</td>
            <td class="table-actions">
              <button class="text-button" @click="editProduct(product)">Editar</button>
              <button class="text-button text-button--danger" @click="removeProduct(product.id_producto)">Eliminar</button>
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
const products = ref([]);
const editingId = ref(null);
const form = reactive({
  id_categoria: null,
  id_proveedor: null,
  sku: "",
  nombre: "",
  descripcion: "",
  precio_unitario: 0,
  stock_actual: 0,
  activo: true,
});

function resetForm() {
  editingId.value = null;
  Object.assign(form, {
    id_categoria: categories.value[0]?.id_categoria || null,
    id_proveedor: null,
    sku: "",
    nombre: "",
    descripcion: "",
    precio_unitario: 0,
    stock_actual: 0,
    activo: true,
  });
}

async function loadData() {
  const [categoryPayload, productPayload] = await Promise.all([
    apiRequest("/api/admin/categories"),
    apiRequest("/api/admin/products"),
  ]);
  categories.value = categoryPayload.items;
  products.value = productPayload.items;
  if (!form.id_categoria) resetForm();
}

function editProduct(product) {
  editingId.value = product.id_producto;
  Object.assign(form, product);
}

async function saveProduct() {
  const payload = { ...form, id_proveedor: form.id_proveedor || null };
  if (editingId.value) {
    await apiRequest(`/api/admin/products/${editingId.value}`, { method: "PUT", body: payload });
  } else {
    await apiRequest("/api/admin/products", { method: "POST", body: payload });
  }
  await loadData();
  resetForm();
}

async function removeProduct(productId) {
  await apiRequest(`/api/admin/products/${productId}`, { method: "DELETE" });
  await loadData();
}

onMounted(loadData);
</script>

