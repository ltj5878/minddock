<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  NSpace,
  NInput,
  NButton,
  NIcon,
  NTabs,
  NTabPane,
  NModal,
  NCard,
  NForm,
  NFormItem,
  NCheckbox,
  NAlert,
  NText,
} from 'naive-ui'
import { SearchOutline, AddOutline, LinkOutline } from '@vicons/ionicons5'
import { useNotesStore } from '../stores/notes'
import NoteCard from '../components/notes/NoteCard.vue'
import type { CaptureNoteResponse } from '../types'

const notesStore = useNotesStore()

const noteTypes = [
  { label: '全部', value: null },
  { label: '笔记', value: 'note' },
  { label: '灵感', value: 'idea' },
  { label: '参考', value: 'reference' },
  { label: '会议', value: 'meeting' },
  { label: '日记', value: 'journal' },
]

const activeTab = ref<string>('all')
const showCaptureModal = ref(false)
const captureTitle = ref('')
const captureContent = ref('')
const writeToNotion = ref(true)
const captureResult = ref<CaptureNoteResponse | null>(null)
const captureError = ref('')
const syncMessage = ref('')
const submitting = ref(false)
const syncing = ref(false)

onMounted(() => {
  if (!notesStore.loaded) {
    notesStore.loadNotes()
  }
})

function handleTabChange(value: string) {
  activeTab.value = value
  notesStore.setFilterType(value === 'all' ? null : value)
}

async function handleCapture() {
  if (!captureContent.value.trim()) return
  submitting.value = true
  captureError.value = ''
  captureResult.value = null
  try {
    captureResult.value = await notesStore.captureNote({
      title: captureTitle.value.trim() || undefined,
      content: captureContent.value.trim(),
      writeToNotion: writeToNotion.value,
    })
    captureTitle.value = ''
    captureContent.value = ''
  } catch (error) {
    captureError.value = error instanceof Error ? error.message : '保存失败'
  } finally {
    submitting.value = false
  }
}

async function handleSyncNotion() {
  syncing.value = true
  syncMessage.value = ''
  try {
    const result = await notesStore.syncNotion()
    syncMessage.value = `Notion 同步完成：导入 ${result.imported}，更新 ${result.updated}，生成 ${result.embeddedChunks} 个 chunk。`
    if (result.warnings.length) syncMessage.value += ` ${result.warnings[0]}`
  } catch (error) {
    syncMessage.value = `Notion 同步失败：${error instanceof Error ? error.message : 'unknown error'}`
  } finally {
    syncing.value = false
  }
}
</script>

<template>
  <div class="inbox-view">
    <div class="inbox-header">
      <h2 style="font-size: 20px; font-weight: 600">收集箱</h2>
      <n-space :size="8">
        <n-button size="small" secondary :loading="syncing" @click="handleSyncNotion">
          <template #icon><n-icon><LinkOutline /></n-icon></template>
          同步 Notion
        </n-button>
        <n-button type="primary" size="small" @click="showCaptureModal = true">
          <template #icon><n-icon><AddOutline /></n-icon></template>
          新建笔记
        </n-button>
      </n-space>
    </div>

    <div class="inbox-search">
      <n-input
        :value="notesStore.searchQuery"
        @update:value="notesStore.setSearchQuery"
        placeholder="搜索笔记..."
        clearable
        size="small"
      >
        <template #prefix>
          <n-icon><SearchOutline /></n-icon>
        </template>
      </n-input>
    </div>

    <n-alert v-if="syncMessage" type="info" style="margin-bottom: 12px">
      {{ syncMessage }}
    </n-alert>

    <n-tabs type="line" :value="activeTab" @update:value="handleTabChange" size="small">
      <n-tab-pane v-for="t in noteTypes" :key="t.value ?? 'all'" :name="t.value ?? 'all'" :tab="t.label">
      </n-tab-pane>
    </n-tabs>

    <div class="notes-grid">
      <NoteCard
        v-for="note in notesStore.filteredNotes"
        :key="note.id"
        :note="note"
      />
      <div v-if="!notesStore.filteredNotes.length" class="empty-state">
        没有找到笔记。试试调整筛选条件或新建一条笔记。
      </div>
    </div>

    <n-modal v-model:show="showCaptureModal">
      <n-card
        title="新建笔记"
        class="capture-modal"
        :bordered="false"
        role="dialog"
        aria-modal="true"
      >
        <n-form label-placement="top">
          <n-form-item label="标题">
            <n-input v-model:value="captureTitle" placeholder="可选，留空由 AI 生成" />
          </n-form-item>
          <n-form-item label="内容">
            <n-input
              v-model:value="captureContent"
              type="textarea"
              placeholder="输入要保存到 MindDock 的内容..."
              :autosize="{ minRows: 8, maxRows: 14 }"
            />
          </n-form-item>
          <n-form-item>
            <n-checkbox v-model:checked="writeToNotion">同步创建 Notion 页面</n-checkbox>
          </n-form-item>
        </n-form>

        <n-alert v-if="captureError" type="error" style="margin-bottom: 12px">
          {{ captureError }}
        </n-alert>

        <n-alert v-if="captureResult" type="success" style="margin-bottom: 12px">
          已保存到本地数据库：{{ captureResult.note.title }}
          <template v-if="captureResult.notion.synced && captureResult.notion.url">
            <br />
            <a :href="captureResult.notion.url" target="_blank" rel="noreferrer">打开 Notion 页面</a>
          </template>
          <template v-else-if="captureResult.warnings.length">
            <br />
            <n-text depth="3">{{ captureResult.warnings[0] }}</n-text>
          </template>
        </n-alert>

        <template #footer>
          <div class="modal-footer">
            <n-button size="small" @click="showCaptureModal = false">关闭</n-button>
            <n-button
              type="primary"
              size="small"
              :loading="submitting"
              :disabled="!captureContent.trim()"
              @click="handleCapture"
            >
              保存
            </n-button>
          </div>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<style scoped>
.inbox-view {
  max-width: 900px;
}

.inbox-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.inbox-search {
  margin-bottom: 12px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px;
  color: var(--color-text-secondary);
}

.capture-modal {
  width: min(720px, calc(100vw - 32px));
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
