import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const sidebarCollapsed = ref(false)
  const contextPanelOpen = ref(false)
  const selectedNoteId = ref<string | null>(null)

  function openContextPanel(noteId: string) {
    selectedNoteId.value = noteId
    contextPanelOpen.value = true
  }

  function closeContextPanel() {
    selectedNoteId.value = null
    contextPanelOpen.value = false
  }

  function toggleContextPanel() {
    contextPanelOpen.value = !contextPanelOpen.value
    if (!contextPanelOpen.value) {
      selectedNoteId.value = null
    }
  }

  return {
    sidebarCollapsed,
    contextPanelOpen,
    selectedNoteId,
    openContextPanel,
    closeContextPanel,
    toggleContextPanel,
  }
})
