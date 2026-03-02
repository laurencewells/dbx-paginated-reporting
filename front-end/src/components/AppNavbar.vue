<script setup lang="ts">
import { RouterLink } from 'vue-router'
import databricksLogo from '@/assets/databricks-symbol-light.webp'

defineProps<{
  sidebarCollapsed?: boolean
}>()

const emit = defineEmits<{
  (e: 'toggle-sidebar'): void
}>()

const navItems = [
  { path: '/', label: 'Home', icon: 'bi-house' },
  { path: '/data-structures', label: 'Data Structures', icon: 'bi-diagram-3' },
  { path: '/template-editor', label: 'Template Editor', icon: 'bi-code-square' },
  { path: '/preview', label: 'Preview & Export', icon: 'bi-file-earmark-pdf' },
  { path: '/guide', label: 'Guide', icon: 'bi-book' },
]
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark fixed-top">
    <div class="container-fluid">
      <button class="btn btn-link text-white me-2 d-lg-none" @click="emit('toggle-sidebar')">
        <i class="bi bi-list fs-4"></i>
      </button>
      <RouterLink class="navbar-brand d-flex align-items-center" to="/">
        <img :src="databricksLogo" alt="Databricks" class="navbar-logo me-2" />
        <span>Paginated Reporting</span>
      </RouterLink>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li v-for="item in navItems" :key="item.path" class="nav-item">
            <RouterLink class="nav-link" :to="item.path" active-class="active">
              <i :class="['bi', item.icon, 'me-1']"></i>
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  height: var(--pr-navbar-height);
  background-color: var(--databricks-dark-blue) !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.navbar-brand {
  font-size: 1.25rem;
}

.navbar-logo {
  height: 28px;
  width: auto;
}

.nav-link {
  padding: 0.5rem 1rem !important;
  border-radius: 6px;
  margin: 0 0.25rem;
  transition: background 0.2s ease;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.2);
  font-weight: 500;
}
</style>
