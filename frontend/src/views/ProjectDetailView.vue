<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NText, NTag, NSpace, NButton, NIcon, NCard, NTabs, NTabPane, NProgress, NTimeline, NTimelineItem, NAlert, NPopconfirm, NModal, NForm, NFormItem, NInput, NSelect, useMessage } from 'naive-ui'
import { ArrowBackOutline, TrashOutline, CheckmarkCircleOutline, AddOutline } from '@vicons/ionicons5'
import { useProjectsStore } from '../stores/projects'
import { useNotesStore } from '../stores/notes'
import NoteCard from '../components/notes/NoteCard.vue'
import type { ProjectAssistant } from '../types'

const route = useRoute()
const router = useRouter()
const projectsStore = useProjectsStore()
const notesStore = useNotesStore()
const message = useMessage()

const projectId = computed(() => route.params.id as string)
const project = computed(() => projectsStore.getProjectById(projectId.value))
const projectNotes = computed(() => notesStore.getNotesByProject(projectId.value))
const projectTasks = computed(() => projectsStore.getTasksByProject(projectId.value))
const assistant = ref<ProjectAssistant | null>(null)
const assistantLoading = ref(false)

const showTaskModal = ref(false)
const creatingTask = ref(false)
const newTask = ref({ title: '', priority: 'medium' })

const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' },
]

const taskProgress = computed(() => {
  if (!projectTasks.value.length) return 0
  const done = projectTasks.value.filter((t: any) => t.status === 'done').length
  return Math.round((done / projectTasks.value.length) * 100)
})

const statusColors: Record<string, string> = {
  todo: 'default',
  in_progress: 'info',
  done: 'success',
  cancelled: 'error',
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

async function loadAssistant() {
  if (!projectId.value) return
  assistantLoading.value = true
  try {
    assistant.value = await projectsStore.getProjectAssistant(projectId.value)
  } finally {
    assistantLoading.value = false
  }
}

async function handleGenerateTasks() {
  await projectsStore.generateTasks(projectId.value)
  await loadAssistant()
  message.success('已根据笔记自动生成任务')
}

async function handleDeleteProject() {
  try {
    await projectsStore.deleteProject(projectId.value)
    message.success('项目已删除')
    router.push('/projects')
  } catch (error) {
    message.error('删除项目失败')
  }
}

async function handleCreateTask() {
  if (!newTask.value.title.trim()) {
    message.warning('请输入任务标题')
    return
  }
  creatingTask.value = true
  try {
    await projectsStore.createTask({
      projectId: projectId.value,
      title: newTask.value.title.trim(),
      priority: newTask.value.priority as any,
      status: 'todo'
    })
    message.success('任务已创建')
    showTaskModal.value = false
    newTask.value = { title: '', priority: 'medium' }
  } catch (error) {
    message.error('创建任务失败')
  } finally {
    creatingTask.value = false
  }
}

async function handleToggleTaskStatus(taskId: string, currentStatus: string) {
  const newStatus = currentStatus === 'done' ? 'todo' : 'done'
  try {
    await projectsStore.updateTask(taskId, { status: newStatus as any })
  } catch (error) {
    message.error('更新任务状态失败')
  }
}

async function handleDeleteTask(taskId: string) {
  try {
    await projectsStore.deleteTask(taskId)
    message.success('任务已删除')
  } catch (error) {
    message.error('删除任务失败')
  }
}

onMounted(async () => {
  if (!projectsStore.loaded) await projectsStore.loadProjects()
  if (!notesStore.loaded) await notesStore.loadNotes()
  await loadAssistant()
})

watch(projectId, loadAssistant)
</script>

<template>
  <div class="project-detail" v-if="project">
    <n-space justify="space-between" align="center" style="margin-bottom: 12px">
      <n-button text @click="router.push('/projects')">
        <template #icon><n-icon><ArrowBackOutline /></n-icon></template>
        返回项目列表
      </n-button>
      <n-popconfirm @positive-click="handleDeleteProject">
        <template #trigger>
          <n-button size="small" type="error" ghost>
            <template #icon><n-icon><TrashOutline /></n-icon></template>
            删除项目
          </n-button>
        </template>
        确定要删除这个项目吗？相关的笔记和任务将被解绑或删除。
      </n-popconfirm>
    </n-space>

    <div class="project-header">
      <div>
        <h2 style="font-size: 22px; font-weight: 600; margin-bottom: 4px">{{ project.name }}</h2>
        <n-text depth="3">{{ project.goal }}</n-text>
      </div>
      <n-tag :type="(statusColors[project.status] || 'default') as any" round>{{ project.status }}</n-tag>
    </div>

    <n-card size="small" style="margin: 16px 0">
      <n-space justify="space-between" align="center">
        <n-space :size="24">
          <n-text style="font-size: 13px"><strong>{{ projectNotes.length }}</strong> 条笔记</n-text>
          <n-text style="font-size: 13px"><strong>{{ projectTasks.length }}</strong> 个任务</n-text>
          <n-text style="font-size: 13px"><strong>{{ taskProgress }}%</strong> 已完成</n-text>
        </n-space>
        <n-button size="small" secondary :loading="assistantLoading" @click="loadAssistant">生成 AI 报告</n-button>
      </n-space>
      <n-progress :percentage="taskProgress" :show-indicator="false" :height="4" style="margin-top: 8px" />
    </n-card>

    <n-tabs type="line" default-value="assistant">
      <n-tab-pane name="assistant" tab="助手">
        <n-alert v-if="assistant" type="info" style="margin-top: 12px">
          {{ assistant.weeklySummary }}
        </n-alert>

        <n-card size="small" title="AI 推荐下一步" style="margin-top: 12px">
          <n-timeline>
            <n-timeline-item
              v-for="action in assistant?.nextActions || []"
              :key="action"
              type="info"
              :title="action"
            />
          </n-timeline>
          <n-button size="small" secondary @click="handleGenerateTasks">一键生成为任务</n-button>
        </n-card>

        <n-space v-if="assistant?.recommendedTags.length" style="margin-top: 12px">
          <n-tag v-for="tag in assistant.recommendedTags" :key="tag" size="small" round>
            {{ tag }}
          </n-tag>
        </n-space>
      </n-tab-pane>

      <n-tab-pane name="notes" tab="笔记">
        <div class="notes-grid">
          <NoteCard v-for="note in projectNotes" :key="note.id" :note="note" />
          <n-text v-if="!projectNotes.length" depth="3">该项目暂无关联笔记。</n-text>
        </div>
      </n-tab-pane>

      <n-tab-pane name="tasks" tab="任务">
        <div style="margin-bottom: 16px; display: flex; justify-content: flex-end;">
          <n-button type="primary" size="small" @click="showTaskModal = true">
            <template #icon><n-icon><AddOutline /></n-icon></template>
            添加任务
          </n-button>
        </div>
        <n-timeline style="margin-top: 12px">
          <n-timeline-item
            v-for="task in projectTasks"
            :key="task.id"
            :type="(statusColors[task.status] as any)"
            :title="task.title"
          >
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <span :style="{ textDecoration: task.status === 'done' ? 'line-through' : 'none', color: task.status === 'done' ? 'gray' : 'inherit' }">{{ task.title }}</span>
                <n-space :size="4">
                  <n-button text size="tiny" @click="handleToggleTaskStatus(task.id, task.status)" :type="task.status === 'done' ? 'default' : 'success'">
                    <template #icon><n-icon><CheckmarkCircleOutline /></n-icon></template>
                  </n-button>
                  <n-popconfirm @positive-click="handleDeleteTask(task.id)">
                    <template #trigger>
                      <n-button text size="tiny" type="error">
                        <template #icon><n-icon><TrashOutline /></n-icon></template>
                      </n-button>
                    </template>
                    确定删除该任务吗？
                  </n-popconfirm>
                </n-space>
              </div>
            </template>
            <n-space :size="8">
              <n-tag size="tiny" round>{{ task.priority }}</n-tag>
              <n-text depth="3" style="font-size: 12px" v-if="task.dueDate">
                截止：{{ formatDate(task.dueDate) }}
              </n-text>
            </n-space>
          </n-timeline-item>
        </n-timeline>
        <n-text v-if="!projectTasks.length" depth="3">该项目暂无任务。</n-text>
      </n-tab-pane>
    </n-tabs>

    <n-modal v-model:show="showTaskModal">
      <n-card style="width: 400px" title="新建任务" :bordered="false" size="huge" role="dialog" aria-modal="true">
        <n-form>
          <n-form-item label="任务标题">
            <n-input v-model:value="newTask.title" placeholder="输入任务名称" />
          </n-form-item>
          <n-form-item label="优先级">
            <n-select v-model:value="newTask.priority" :options="priorityOptions" />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showTaskModal = false">取消</n-button>
            <n-button type="primary" :loading="creatingTask" @click="handleCreateTask">创建</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>

  <div v-else style="text-align: center; padding: 40px">
    <n-text depth="3">项目未找到。</n-text>
  </div>
</template>

<style scoped>
.project-detail {
  max-width: 900px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  margin-top: 12px;
}
</style>
