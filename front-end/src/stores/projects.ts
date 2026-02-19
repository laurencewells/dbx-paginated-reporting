import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'pr-active-project-id'

export const useProjectsStore = defineStore('projects', () => {
  const stored = localStorage.getItem(STORAGE_KEY)
  const activeProjectId = ref<string | null>(stored)

  function setActiveProject(id: string | null) {
    activeProjectId.value = id
  }

  watch(activeProjectId, (v) => {
    if (v) localStorage.setItem(STORAGE_KEY, v)
    else localStorage.removeItem(STORAGE_KEY)
  })

  return {
    activeProjectId,
    setActiveProject,
  }
})
