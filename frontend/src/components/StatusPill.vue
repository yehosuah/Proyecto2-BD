<template>
  <span class="status-pill" :class="statusClass">{{ label }}</span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  value: {
    type: String,
    required: true,
  },
});

const label = computed(() => props.value.replaceAll("_", " "));

const statusClass = computed(() => {
  const value = props.value.toLowerCase();
  if (["aprobado", "completado", "listo_para_retiro", "entregado"].includes(value)) return "status-pill--success";
  if (["rechazado", "cancelado"].includes(value)) return "status-pill--danger";
  if (["en_preparacion", "pendiente"].includes(value)) return "status-pill--warning";
  return "status-pill--neutral";
});
</script>

