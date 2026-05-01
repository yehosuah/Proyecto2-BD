import { computed, reactive } from "vue";

const STORAGE_KEY = "proyecto2-cart";
const RESULT_KEY = "proyecto2-last-order";

export const cartState = reactive({
  loaded: false,
  items: [],
});

function persist() {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cartState.items));
}

export function ensureCartLoaded() {
  if (cartState.loaded || typeof window === "undefined") {
    return;
  }
  const raw = window.localStorage.getItem(STORAGE_KEY);
  cartState.items = raw ? JSON.parse(raw) : [];
  cartState.loaded = true;
}

export function addToCart(product) {
  ensureCartLoaded();
  const existing = cartState.items.find((item) => item.id_producto === product.id_producto);
  if (existing) {
    existing.cantidad += 1;
  } else {
    cartState.items.push({
      id_producto: product.id_producto,
      sku: product.sku,
      nombre: product.nombre,
      precio_unitario: Number(product.precio_unitario),
      cantidad: 1,
    });
  }
  persist();
}

export function updateQuantity(productId, quantity) {
  ensureCartLoaded();
  const item = cartState.items.find((entry) => entry.id_producto === productId);
  if (!item) return;
  if (quantity <= 0) {
    removeFromCart(productId);
    return;
  }
  item.cantidad = quantity;
  persist();
}

export function removeFromCart(productId) {
  ensureCartLoaded();
  cartState.items = cartState.items.filter((entry) => entry.id_producto !== productId);
  persist();
}

export function clearCart() {
  cartState.items = [];
  persist();
}

export function saveLastOrder(payload) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(RESULT_KEY, JSON.stringify(payload));
}

export function getLastOrder() {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(RESULT_KEY);
  return raw ? JSON.parse(raw) : null;
}

export const cartTotal = computed(() =>
  cartState.items.reduce((sum, item) => sum + Number(item.precio_unitario) * item.cantidad, 0),
);

