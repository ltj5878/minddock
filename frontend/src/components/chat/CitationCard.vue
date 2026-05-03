<script setup lang="ts">
import { NText, NIcon } from 'naive-ui'
import { DocumentTextOutline } from '@vicons/ionicons5'
import type { Citation } from '../../types'
import { useUiStore } from '../../stores/ui'

defineProps<{
  citation: Citation
  index: number
}>()

const ui = useUiStore()

function handleClick(noteId: string) {
  ui.openContextPanel(noteId)
}
</script>

<template>
  <div class="citation-card" @click="handleClick(citation.noteId)">
    <div class="citation-header">
      <n-icon size="14"><DocumentTextOutline /></n-icon>
      <n-text style="font-size: 12px; font-weight: 500">[{{ index }}] {{ citation.noteTitle }}</n-text>
    </div>
    <n-text depth="3" style="font-size: 11px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
      {{ citation.chunkText }}
    </n-text>
    <n-text depth="3" style="font-size: 10px; margin-top: 4px">
      相似度：{{ (citation.similarity * 100).toFixed(0) }}%
    </n-text>
  </div>
</template>

<style scoped>
.citation-card {
  background: #f8f9fa;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  cursor: pointer;
  transition: background 0.15s;
}

.citation-card:hover {
  background: #f0f1f3;
}

.citation-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}
</style>
