import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Project, ProjectAssistant, Task } from '../types'
import mockProjects from '../mock/projects.json'
import mockTasks from '../mock/tasks.json'
import client from '../api/client'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref<Project[]>(mockProjects as Project[])
  const tasks = ref<Task[]>(mockTasks as Task[])
  const loading = ref(false)
  const loaded = ref(false)

  function getProjectById(id: string): Project | undefined {
    return projects.value.find((p) => p.id === id)
  }

  function getTasksByProject(projectId: string): Task[] {
    return tasks.value.filter((t) => t.projectId === projectId)
  }

  const activeProjects = computed(() =>
    projects.value.filter((p) => p.status === 'active')
  )

  const pendingTasks = computed(() =>
    tasks.value.filter((t) => t.status === 'todo' || t.status === 'in_progress')
  )

  async function loadProjects() {
    loading.value = true
    try {
      const { data } = await client.get<{ projects: Project[]; tasks: Task[] }>('/projects')
      projects.value = data.projects
      tasks.value = data.tasks
      loaded.value = true
    } catch (error) {
      console.warn('Failed to load local database projects, using mock data.', error)
      projects.value = mockProjects as Project[]
      tasks.value = mockTasks as Task[]
    } finally {
      loading.value = false
    }
  }

  async function getProjectAssistant(projectId: string): Promise<ProjectAssistant> {
    const { data } = await client.get<ProjectAssistant>(`/projects/${projectId}/assistant`)
    return data
  }

  async function generateTasks(projectId: string): Promise<Task[]> {
    const { data } = await client.post<{ created: number; tasks: Task[] }>(
      `/projects/${projectId}/tasks/generate`
    )
    tasks.value = [...data.tasks, ...tasks.value]
    return data.tasks
  }

  async function createProject(payload: Partial<Project>): Promise<Project> {
    const { data } = await client.post<Project>('/projects', payload)
    projects.value.unshift(data)
    return data
  }

  async function updateProject(id: string, payload: Partial<Project>): Promise<Project> {
    const { data } = await client.patch<Project>(`/projects/${id}`, payload)
    projects.value = projects.value.map((p) => (p.id === id ? data : p))
    return data
  }

  async function deleteProject(id: string) {
    await client.delete(`/projects/${id}`)
    projects.value = projects.value.filter((p) => p.id !== id)
  }

  async function createTask(payload: Partial<Task>): Promise<Task> {
    const { data } = await client.post<Task>('/projects/tasks', payload)
    tasks.value.unshift(data)
    return data
  }

  async function updateTask(id: string, payload: Partial<Task>): Promise<Task> {
    const { data } = await client.patch<Task>(`/projects/tasks/${id}`, payload)
    tasks.value = tasks.value.map((t) => (t.id === id ? data : t))
    return data
  }

  async function deleteTask(id: string) {
    await client.delete(`/projects/tasks/${id}`)
    tasks.value = tasks.value.filter((t) => t.id !== id)
  }

  return {
    projects,
    tasks,
    loading,
    loaded,
    getProjectById,
    getTasksByProject,
    loadProjects,
    getProjectAssistant,
    generateTasks,
    createProject,
    updateProject,
    deleteProject,
    createTask,
    updateTask,
    deleteTask,
    activeProjects,
    pendingTasks,
  }
})
