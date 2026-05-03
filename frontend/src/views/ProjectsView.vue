<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { NCard, NText, NTag, NSpace, NButton, NIcon, NProgress, NModal, NForm, NFormItem, NInput, useMessage } from 'naive-ui'
import { AddOutline } from '@vicons/ionicons5'
import { useProjectsStore } from '../stores/projects'
import { useNotesStore } from '../stores/notes'
import { useRouter } from 'vue-router'

const projectsStore = useProjectsStore()
const notesStore = useNotesStore()
const router = useRouter()
const message = useMessage()

const showCreateModal = ref(false)
const creating = ref(false)
const newProject = ref({
  name: '',
  goal: '',
})

onMounted(() => {
  if (!projectsStore.loaded) projectsStore.loadProjects()
  if (!notesStore.loaded) notesStore.loadNotes()
})

function getProjectNoteCount(projectId: string): number {
  return notesStore.getNotesByProject(projectId).length
}

function getProjectTaskProgress(projectId: string): number {
  const tasks = projectsStore.getTasksByProject(projectId)
  if (!tasks.length) return 0
  const done = tasks.filter((t) => t.status === 'done').length
  return Math.round((done / tasks.length) * 100)
}

function navigateToProject(id: string) {
  router.push(`/projects/${id}`)
}

async function handleCreateProject() {
  if (!newProject.value.name.trim()) {
    message.warning('请输入项目名称')
    return
  }
  
  creating.value = true
  try {
    await projectsStore.createProject({
      name: newProject.value.name.trim(),
      goal: newProject.value.goal.trim(),
      status: 'active'
    })
    message.success('项目创建成功')
    showCreateModal.value = false
    newProject.value = { name: '', goal: '' }
  } catch (error) {
    message.error('项目创建失败')
  } finally {
    creating.value = false
  }
}

const statusColors: Record<string, string> = {
  active: 'success',
  paused: 'warning',
  completed: 'info',
  archived: 'default',
}
</script>

<template>
  <div class="projects-view">
    <div class="projects-header">
      <h2 style="font-size: 20px; font-weight: 600">项目</h2>
      <n-button type="primary" size="small" @click="showCreateModal = true">
        <template #icon><n-icon><AddOutline /></n-icon></template>
        新建项目
      </n-button>
    </div>

    <div class="projects-grid">
      <n-card
        v-for="project in projectsStore.projects"
        :key="project.id"
        hoverable
        class="project-card"
        @click="navigateToProject(project.id)"
      >
        <template #header>
          <n-space justify="space-between" align="center">
            <n-text strong>{{ project.name }}</n-text>
            <n-tag :type="(statusColors[project.status] as any)" size="small" round>
              {{ project.status }}
            </n-tag>
          </n-space>
        </template>

        <n-text depth="3" style="font-size: 13px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
          {{ project.goal }}
        </n-text>

        <div class="project-stats">
          <n-space :size="16">
            <n-text depth="3" style="font-size: 12px">
              {{ getProjectNoteCount(project.id) }} 条笔记
            </n-text>
            <n-text depth="3" style="font-size: 12px">
              {{ projectsStore.getTasksByProject(project.id).length }} 个任务
            </n-text>
          </n-space>
          <n-progress
            type="line"
            :percentage="getProjectTaskProgress(project.id)"
            :show-indicator="false"
            :height="4"
            style="margin-top: 8px"
          />
        </div>
      </n-card>
    </div>

    <n-modal v-model:show="showCreateModal">
      <n-card
        style="width: 500px"
        title="新建项目"
        :bordered="false"
        size="huge"
        role="dialog"
        aria-modal="true"
      >
        <n-form>
          <n-form-item label="项目名称">
            <n-input v-model:value="newProject.name" placeholder="输入项目名称" />
          </n-form-item>
          <n-form-item label="项目目标">
            <n-input
              v-model:value="newProject.goal"
              type="textarea"
              placeholder="一句话描述这个项目的目标..."
              :autosize="{ minRows: 3, maxRows: 5 }"
            />
          </n-form-item>
        </n-form>
        <template #footer>
          <n-space justify="end">
            <n-button @click="showCreateModal = false">取消</n-button>
            <n-button type="primary" :loading="creating" @click="handleCreateProject">创建</n-button>
          </n-space>
        </template>
      </n-card>
    </n-modal>
  </div>
</template>

<style scoped>
.projects-view {
  max-width: 900px;
}

.projects-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.project-card {
  cursor: pointer;
  transition: box-shadow 0.2s;
}

.project-card:hover {
  box-shadow: var(--shadow-md);
}

.project-stats {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-border);
}
</style>
