<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { NText, NSpace, NTag, NDivider, NSelect, useMessage } from 'naive-ui'
import type { Note } from '../../types'
import TagBadge from '../common/TagBadge.vue'
import MarkdownRenderer from '../common/MarkdownRenderer.vue'
import { useNotesStore } from '../../stores/notes'
import { useProjectsStore } from '../../stores/projects'

const props = defineProps<{
  note: Note
}>()

const notesStore = useNotesStore()
const projectsStore = useProjectsStore()
const message = useMessage()

const localProjectId = ref<string | null>(props.note.projectId)
const updating = ref(false)

watch(() => props.note.projectId, (newVal) => {
  localProjectId.value = newVal
})

const projectOptions = computed(() => {
  const options = projectsStore.activeProjects.map(p => ({
    label: p.name,
    value: p.id
  }))
  options.unshift({ label: '未归档', value: null as any })
  return options
})

async function handleProjectChange(val: string | null) {
  localProjectId.value = val
  updating.value = true
  try {
    await notesStore.updateNote(props.note.id, { projectId: val })
    message.success('已更新归属项目')
  } catch (error) {
    message.error('更新归属项目失败')
    localProjectId.value = props.note.projectId // revert
  } finally {
    updating.value = false
  }
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
  return new Date(dateStr).toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="note-detail">
    <n-text tag="h3" style="font-size: 16px; font-weight: 600; margin-bottom: 8px">
      {{ note.title }}
    </n-text>

    <n-space :size="8" style="margin-bottom: 12px" align="center">
      <n-tag size="small" round>{{ typeLabels[note.type] }}</n-tag>
      <n-text depth="3" style="font-size: 12px">{{ formatDate(note.createdAt) }}</n-text>
    </n-space>

    <div style="margin-bottom: 16px">
      <n-text depth="3" style="font-size: 12px; margin-bottom: 4px; display: block">归属项目</n-text>
      <n-select
        v-model:value="localProjectId"
        :options="projectOptions"
        size="small"
        :disabled="updating"
        @update:value="handleProjectChange"
        placeholder="选择关联项目..."
      />
    </div>

    <div v-if="note.tags.length" style="margin-bottom: 12px">
      <TagBadge v-for="tag in note.tags" :key="tag" :tag="tag" />
    </div>

    <div v-if="note.summary" style="margin-bottom: 12px">
      <n-text depth="3" style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px">摘要</n-text>
      <n-text tag="p" style="font-size: 13px; color: var(--color-text-secondary); margin-top: 4px">
        {{ note.summary }}
      </n-text>
    </div>

    <n-divider style="margin: 12px 0" />

    <MarkdownRenderer :content="note.content" />

    <div v-if="note.actionItems?.length" style="margin-top: 16px">
      <n-divider style="margin: 12px 0" />
      <n-text depth="3" style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px">行动项</n-text>
      <ul style="padding-left: 16px; margin-top: 8px">
        <li v-for="(item, i) in note.actionItems" :key="i" style="font-size: 13px; margin-bottom: 4px">
          {{ item }}
        </li>
      </ul>
    </div>

    <div v-if="note.sourceUrl" style="margin-top: 12px">
      <n-text depth="3" style="font-size: 12px">
        来源：<a :href="note.sourceUrl" target="_blank">{{ note.sourceUrl }}</a>
      </n-text>
    </div>
  </div>
</template>

<style scoped>
.note-detail {
  padding: 4px;
}
</style>
