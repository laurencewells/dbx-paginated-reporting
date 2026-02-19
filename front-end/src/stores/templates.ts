import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTemplatesStore = defineStore('templates', () => {
  const activeTemplateId = ref<string | null>(null)

  function setActiveTemplate(id: string | null) {
    activeTemplateId.value = id
  }

  return {
    activeTemplateId,
    setActiveTemplate,
  }
})
