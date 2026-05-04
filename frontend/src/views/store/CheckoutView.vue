<template>
  <div class="checkout-grid">
    <article class="card-surface">
      <div class="section-header">
        <div>
          <h1>Checkout</h1>
          <p class="muted-copy">Compra como invitado o usa tu sesion para guardar el pedido.</p>
        </div>
        <StatusPill :value="statusLabel" />
      </div>

      <form class="form-grid" @submit.prevent="submitCheckout">
        <label class="form-field">
          <span>Nombre</span>
          <input v-model="form.customer.nombre" class="field" required />
        </label>
        <label class="form-field">
          <span>Email</span>
          <input v-model="form.customer.email" class="field" required />
        </label>
        <label class="form-field">
          <span>Telefono</span>
          <input v-model="form.customer.telefono" class="field" />
        </label>
        <label class="form-field">
          <span>Tipo de entrega</span>
          <select v-model="form.tipo_entrega" class="field">
            <option value="pickup">Pickup</option>
            <option value="delivery">Delivery</option>
          </select>
        </label>
        <label class="form-field full-width">
          <span>Nota</span>
          <textarea v-model="form.nota_cliente" class="field field--textarea"></textarea>
        </label>

        <template v-if="form.tipo_entrega === 'delivery'">
          <label class="form-field full-width">
            <span>Direccion</span>
            <input v-model="form.direccion.linea_1" class="field" required />
          </label>
          <label class="form-field">
            <span>Ciudad</span>
            <input v-model="form.direccion.ciudad" class="field" required />
          </label>
          <label class="form-field">
            <span>Departamento</span>
            <input v-model="form.direccion.departamento" class="field" required />
          </label>
          <label class="form-field full-width">
            <span>Referencia</span>
            <input v-model="form.direccion.referencia" class="field" />
          </label>
        </template>

        <label class="form-field">
          <span>Metodo de pago</span>
          <select v-model="form.payment.metodo" class="field">
            <option value="efectivo">Efectivo</option>
            <option value="tarjeta">Tarjeta</option>
            <option value="transferencia">Transferencia</option>
          </select>
        </label>
        <label class="form-field">
          <span>Referencia simulada</span>
          <input v-model="form.payment.referencia" class="field" required />
        </label>

        <div class="info-strip full-width">
          <strong>Regla demo:</strong> una referencia con `FAIL` o que termine en `0000` rechaza el pago.
        </div>

        <p v-if="error" class="error-banner full-width">{{ error }}</p>

        <div class="hero-copy__actions full-width">
          <button class="button button--accent" :disabled="submitting || !cartItems.length">
            {{ submitting ? "Procesando..." : "Confirmar compra" }}
          </button>
        </div>
      </form>
    </article>

    <aside class="card-surface">
      <div class="card-header">
        <h2>Resumen</h2>
        <span>{{ cartItems.length }} productos</span>
      </div>
      <div class="mini-cart">
        <div v-for="item in cartItems" :key="item.id_producto" class="mini-cart__row">
          <div>
            <p>{{ item.nombre }}</p>
            <small>{{ money(item.precio_unitario) }} x {{ item.cantidad }}</small>
          </div>
          <div class="mini-cart__controls">
            <button class="icon-button" @click="updateQuantity(item.id_producto, item.cantidad - 1)">−</button>
            <span>{{ item.cantidad }}</span>
            <button class="icon-button" @click="updateQuantity(item.id_producto, item.cantidad + 1)">+</button>
          </div>
        </div>
      </div>
      <div class="mini-cart__footer">
        <strong>Total</strong>
        <strong>{{ money(cartTotal) }}</strong>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";

import StatusPill from "../../components/StatusPill.vue";
import { apiRequest } from "../../lib/api";
import {
  cartState,
  cartTotal,
  clearCart,
  ensureCartLoaded,
  saveLastOrder,
  updateQuantity,
} from "../../stores/cart";
import { ensureSessionLoaded, sessionState } from "../../stores/session";

const router = useRouter();
const submitting = ref(false);
const error = ref("");
const statusLabel = ref("pendiente");
const form = reactive({
  customer: { nombre: "", email: "", telefono: "" },
  tipo_entrega: "pickup",
  nota_cliente: "",
  direccion: { linea_1: "", ciudad: "", departamento: "", referencia: "" },
  payment: { metodo: "efectivo", referencia: "EFECTIVO-OK" },
});

const cartItems = computed(() => cartState.items);

function money(value) {
  return new Intl.NumberFormat("es-GT", { style: "currency", currency: "GTQ" }).format(value);
}

async function submitCheckout() {
  submitting.value = true;
  error.value = "";
  statusLabel.value = "validando";
  try {
    const payload = await apiRequest("/api/orders/checkout", {
      method: "POST",
      body: {
        customer: form.customer,
        tipo_entrega: form.tipo_entrega,
        nota_cliente: form.nota_cliente,
        direccion: form.tipo_entrega === "delivery" ? form.direccion : null,
        items: cartItems.value.map((item) => ({
          id_producto: item.id_producto,
          cantidad: item.cantidad,
        })),
        payment: form.payment,
      },
    });
    statusLabel.value = "aprobado";
    saveLastOrder(payload);
    clearCart();
    router.push(`/checkout/resultado/${payload.order.codigo_publico}`);
  } catch (requestError) {
    try {
      const parsed = JSON.parse(requestError.message);
      if (parsed.payment?.estado === "rechazado") {
        statusLabel.value = "rechazado";
        error.value = parsed.payment.motivo;
        return;
      }
    } catch {
      // no-op
    }
    statusLabel.value = "error";
    error.value = requestError.message;
  } finally {
    submitting.value = false;
  }
}

onMounted(async () => {
  ensureCartLoaded();
  await ensureSessionLoaded();
  if (sessionState.user) {
    form.customer.nombre = `${sessionState.user.nombre} ${sessionState.user.apellido}`;
    form.customer.email = sessionState.user.email;
    form.customer.telefono = sessionState.user.telefono || "";
  }
});
</script>

