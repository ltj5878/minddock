<script setup lang="ts">
import { NCard, NText, NSpace, NTag, NIcon, NButton, NPopconfirm } from 'naive-ui'
import { TimeOutline, TrashOutline } from '@vicons/ionicons5'
import type { Note } from '../../types'
import TagBadge from '../common/TagBadge.vue'
import { useUiStore } from '../../stores/ui'
import { useNotesStore } from '../../stores/notes'

const props = defineProps<{
  note: Note
}>()

const ui = useUiStore()
const notesStore = useNotesStore()

const typeColors: Record<string, string> = {
  note: 'default',
  idea: 'warning',
  reference: 'info',
  meeting: 'success',
  journal: 'primary',
  task_note: 'error',
}

const typeLabels: Record<string, string> = {
  note: '笔记',
  idea: '灵感',
  reference: '参考',
  meeting: '会议',
  journal: '日记',
  task_note: '任务笔记',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

function handleClick() {
  ui.openContextPanel(props.note.id)
}

async function handleDelete() {
  await notesStore.deleteNote(props.note.id)
}
</script>

<template>
  <n-card
    hoverable
    size="small"
    class="note-card"
    @click="handleClick"
  >
    <template #header>
      <div class="note-header">
        <n-text strong style="font-size: 14px">{{ note.title }}</n-text>
        <n-space :size="8" align="center">
          <n-tag :type="(typeColors[note.type] as any)" size="tiny" round>
            {{ typeLabels[note.type] }}
          </n-tag>
          <n-popconfirm @positive-click="handleDelete" @click.stop>
            <template #trigger>
              <n-button text size="tiny" @click.stop>
                <template #icon><n-icon><TrashOutline /></n-icon></template>
              </n-button>
            </template>
            确定要删除这条笔记吗？
          </n-popconfirm>
        </n-space>
      </div>
    </template>
    <n-text depth="3" style="font-size: 13px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
      {{ note.summary || note.content.slice(0, 120) }}
    </n-text>
    <div class="note-footer">
      <n-space :size="4" align="center">
        <TagBadge v-for="tag in note.tags.slice(0, 3)" :key="tag" :tag="tag" />
        <n-text v-if="note.tags.length > 3" depth="3" style="font-size: 12px">
          +{{ note.tags.length - 3 }}
        </n-text>
      </n-space>
      <n-space :size="4" align="center">
        <n-icon size="14" depth="3"><TimeOutline /></n-icon>
        <n-text depth="3" style="font-size: 12px">{{ formatDate(note.createdAt) }}</n-text>
      </n-space>
    </div>
  </n-card>
</template>

<style scoped>
.note-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.note-card:hover {
  box-shadow: var(--shadow-md);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}
</style>
