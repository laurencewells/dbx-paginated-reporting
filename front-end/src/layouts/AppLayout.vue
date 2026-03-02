<script setup lang="ts">
import { ref } from 'vue'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import ToastContainer from '@/components/ToastContainer.vue'

const sidebarCollapsed = ref(false)

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

</script>

<template>
  <div class="app-wrapper" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <AppNavbar @toggle-sidebar="toggleSidebar" :sidebar-collapsed="sidebarCollapsed" />
    <AppSidebar :collapsed="sidebarCollapsed" @toggle="toggleSidebar" />
    <main class="app-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <slot />
    </main>
    <ToastContainer />
  </div>
</template>

<style scoped>
.app-wrapper {
  min-height: 100vh;
}
</style>
