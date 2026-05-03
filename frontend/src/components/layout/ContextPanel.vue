<script setup lang="ts">
import { computed } from 'vue'
import { NEmpty, NButton, NScrollbar } from 'naive-ui'
import { useUiStore } from '../../stores/ui'
import { useNotesStore } from '../../stores/notes'
import NoteDetail from '../notes/NoteDetail.vue'

const ui = useUiStore()
const notesStore = useNotesStore()

const selectedNote = computed(() => {
  if (!ui.selectedNoteId) return null
  return notesStore.getNoteById(ui.selectedNoteId)
})
</script>

<template>
  <div class="context-panel">
    <div class="panel-header">
      <span>详情</span>
      <n-button text @click="ui.closeContextPanel">
        &times;
      </n-button>
    </div>
    <n-scrollbar style="flex: 1">
      <div class="panel-content">
        <NoteDetail v-if="selectedNote" :note="selectedNote" />
        <n-empty v-else description="选择一条笔记查看详情" />
      </div>
    </n-scrollbar>
  </div>
</template>

<style scoped>
.context-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  font-weight: 600;
  border-bottom: 1px solid var(--color-border);
}

.panel-content {
  padding: 16px;
}
</style>
