<script setup lang="ts">
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const toasts = computed(() => toastStore.toasts)

function getToastClass(type: string): string {
  const classes: Record<string, string> = {
    success: 'bg-success text-white',
    error: 'bg-danger text-white',
    warning: 'bg-warning text-dark',
    info: 'bg-info text-white',
  }
  return classes[type] || classes.info
}

function getIcon(type: string): string {
  const icons: Record<string, string> = {
    success: 'bi-check-circle-fill',
    error: 'bi-exclamation-triangle-fill',
    warning: 'bi-exclamation-circle-fill',
    info: 'bi-info-circle-fill',
  }
  return icons[type] || icons.info
}
</script>

<template>
  <div class="toast-container" aria-live="polite" aria-atomic="false">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast show mb-2"
        :class="getToastClass(toast.type)"
        role="alert"
      >
        <div class="toast-body d-flex align-items-center">
          <i :class="['bi', getIcon(toast.type), 'me-2']"></i>
          <span class="flex-grow-1">{{ toast.message }}</span>
          <button
            type="button"
            class="btn-close btn-close-white ms-2"
            @click="toastStore.removeToast(toast.id)"
          ></button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: calc(var(--pr-navbar-height) + 1rem);
  right: 1rem;
  z-index: 1100;
  max-width: 350px;
}

.toast {
  min-width: 280px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
