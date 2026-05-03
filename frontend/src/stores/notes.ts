import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CaptureNoteResponse, Note, SyncNotionResponse } from '../types'
import mockNotes from '../mock/notes.json'
import client from '../api/client'

export const useNotesStore = defineStore('notes', () => {
  const notes = ref<Note[]>(mockNotes as Note[])
  const loading = ref(false)
  const loaded = ref(false)
  const filterType = ref<string | null>(null)
  const filterTag = ref<string | null>(null)
  const searchQuery = ref('')

  const filteredNotes = computed(() => {
    let result = notes.value

    if (filterType.value) {
      result = result.filter((n) => n.type === filterType.value)
    }

    if (filterTag.value) {
      result = result.filter((n) => n.tags.includes(filterTag.value!))
    }

    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      result = result.filter(
        (n) =>
          n.title.toLowerCase().includes(q) ||
          n.content.toLowerCase().includes(q) ||
          n.tags.some((t) => t.toLowerCase().includes(q))
      )
    }

    return result.sort(
      (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    )
  })

  const allTags = computed(() => {
    const tagSet = new Set<string>()
    notes.value.forEach((n) => n.tags.forEach((t) => tagSet.add(t)))
    return Array.from(tagSet).sort()
  })

  function getNoteById(id: string): Note | undefined {
    return notes.value.find((n) => n.id === id)
  }

  function getNotesByProject(projectId: string): Note[] {
    return notes.value.filter((n) => n.projectId === projectId)
  }

  async function loadNotes() {
    loading.value = true
    try {
      const { data } = await client.get<{ notes: Note[]; total: number }>('/notes')
      notes.value = data.notes
      loaded.value = true
    } catch (error) {
      console.warn('Failed to load local database notes, using mock data.', error)
      notes.value = mockNotes as Note[]
    } finally {
      loading.value = false
    }
  }

  async function captureNote(payload: {
    content: string
    title?: string
    writeToNotion?: boolean
  }): Promise<CaptureNoteResponse> {
    loading.value = true
    try {
      const { data } = await client.post<CaptureNoteResponse>('/notes/capture', {
        content: payload.content,
        title: payload.title || null,
        sourceType: 'direct',
        writeToNotion: payload.writeToNotion ?? true,
      })
      notes.value = [data.note, ...notes.value.filter((note) => note.id !== data.note.id)]
      loaded.value = true
      return data
    } finally {
      loading.value = false
    }
  }

  async function syncNotion(): Promise<SyncNotionResponse> {
    loading.value = true
    try {
      const { data } = await client.post<SyncNotionResponse>('/notes/sync/notion', {})
      await loadNotes()
      return data
    } finally {
      loading.value = false
    }
  }

  async function deleteNote(id: string) {
    await client.delete(`/notes/${id}`)
    notes.value = notes.value.filter((n) => n.id !== id)
  }

  async function updateNote(id: string, payload: Partial<Note>) {
    const { data } = await client.patch<Note>(`/notes/${id}`, payload)
    notes.value = notes.value.map((n) => (n.id === id ? data : n))
    return data
  }

  async function generateWeeklyReview(): Promise<string> {
    const { data } = await client.get<{ summary: string }>('/review/weekly')
    return data.summary
  }

  function setFilterType(type: string | null) {
    filterType.value = type
  }

  function setFilterTag(tag: string | null) {
    filterTag.value = tag
  }

  function setSearchQuery(query: string) {
    searchQuery.value = query
  }

  return {
    notes,
    loading,
    loaded,
    filterType,
    filterTag,
    searchQuery,
    filteredNotes,
    allTags,
    getNoteById,
    getNotesByProject,
    loadNotes,
    captureNote,
    syncNotion,
    deleteNote,
    updateNote,
    generateWeeklyReview,
    setFilterType,
    setFilterTag,
    setSearchQuery,
  }
})
