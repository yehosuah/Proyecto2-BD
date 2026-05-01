<template>
  <div class="product-visual" :class="toneClass">
    <img class="product-visual__image" :src="imageSrc" :alt="imageAlt" loading="lazy" />
    <span class="product-visual__caption">{{ caption }}</span>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
});

const skuImages = {
  "HOG-001": "/assets/product-photos/sku-hog-001.png",
  "HOG-002": "/assets/product-photos/sku-hog-002.png",
  "COC-001": "/assets/product-photos/sku-coc-001.png",
  "BAN-001": "/assets/product-photos/sku-ban-001.png",
  "TEX-001": "/assets/product-photos/sku-tex-001.png",
  "BIE-001": "/assets/product-photos/sku-bie-001.png",
};

const categoryImages = {
  Hogar: "/assets/product-photos/sku-hog-001.png",
  Cocina: "/assets/product-photos/sku-coc-001.png",
  Decoracion: "/assets/product-photos/hero-home-goods.png",
  "Baño": "/assets/product-photos/sku-ban-001.png",
  Textiles: "/assets/product-photos/sku-tex-001.png",
  Bienestar: "/assets/product-photos/sku-bie-001.png",
  Accesorios: "/assets/product-photos/sku-hog-002.png",
  Organizacion: "/assets/product-photos/sku-hog-002.png",
  Plantas: "/assets/product-photos/sku-hog-001.png",
  Iluminacion: "/assets/product-photos/sku-bie-001.png",
  Mesa: "/assets/product-photos/sku-coc-001.png",
  Limpieza: "/assets/product-photos/sku-ban-001.png",
  Papeleria: "/assets/product-photos/sku-hog-002.png",
  Dormitorio: "/assets/product-photos/sku-tex-001.png",
  Jardin: "/assets/product-photos/sku-hog-001.png",
  "Cuidado personal": "/assets/product-photos/sku-ban-001.png",
  Aromas: "/assets/product-photos/sku-bie-001.png",
  Ceramica: "/assets/product-photos/sku-coc-001.png",
  Madera: "/assets/product-photos/sku-hog-002.png",
  Vidrio: "/assets/product-photos/sku-ban-001.png",
  Regalos: "/assets/product-photos/hero-home-goods.png",
  Temporada: "/assets/product-photos/sku-bie-001.png",
  Mascotas: "/assets/product-photos/sku-tex-001.png",
  Viaje: "/assets/product-photos/sku-hog-002.png",
  Oficina: "/assets/product-photos/sku-coc-001.png",
};

const toneClass = computed(() => {
  const category = props.product.categoria_nombre || props.product.categoria || "default";
  const slug = category
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "-");
  return `product-visual--${slug}`;
});

const imageSrc = computed(() => {
  const category = props.product.categoria_nombre || props.product.categoria;
  return skuImages[props.product.sku] || categoryImages[category] || "/assets/product-photos/hero-home-goods.png";
});

const imageAlt = computed(() => `Foto de ${props.product.nombre || props.product.sku || "producto"}`);
const caption = computed(() => props.product.sku || props.product.nombre);
</script>
