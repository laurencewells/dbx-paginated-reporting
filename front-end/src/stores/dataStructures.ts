import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useDataStructuresStore = defineStore('dataStructures', () => {
  const activeStructureId = ref<string | null>(null)

  function setActiveStructure(id: string | null) {
    activeStructureId.value = id
  }

  return {
    activeStructureId,
    setActiveStructure,
  }
})
