export interface Note {
  id: string
  title: string
  content: string
  summary: string
  type: 'note' | 'idea' | 'reference' | 'meeting' | 'journal' | 'task_note'
  tags: string[]
  projectId: string | null
  sourceUrl: string | null
  sourceType: 'manual' | 'notion_sync' | 'zhihu' | 'yuque' | 'url' | 'direct'
  actionItems: string[]
  notionPageId?: string | null
  notionUrl?: string | null
  classificationProvider?: string
  createdAt: string
  updatedAt: string
}

export interface NoteClassification {
  title: string
  summary: string
  type: Note['type']
  tags: string[]
  action_items: string[]
}

export interface CaptureNoteResponse {
  note: Note
  classification: NoteClassification
  notion: {
    synced: boolean
    page_id: string | null
    url: string | null
    warning: string | null
  }
  warnings: string[]
}

export interface SyncNotionResponse {
  imported: number
  updated: number
  embeddedChunks: number
  warnings: string[]
}

export interface Project {
  id: string
  name: string
  goal: string
  status: 'active' | 'paused' | 'completed' | 'archived'
  notionProjectPageId: string | null
  createdAt: string
  updatedAt: string
}

export interface Task {
  id: string
  title: string
  status: 'todo' | 'in_progress' | 'done' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  dueDate: string | null
  projectId: string | null
  sourceNoteId: string | null
  createdAt: string
  updatedAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  createdAt: string
}

export interface Citation {
  noteId: string
  noteTitle: string
  chunkText: string
  similarity: number
}

export interface DailyReview {
  date: string
  newNotes: Note[]
  pendingTasks: Task[]
  topThemes: string[]
  aiSummary: string
  suggestions: string[]
}

export interface ProjectAssistant {
  project: Project
  noteCount: number
  taskCount: number
  weeklySummary: string
  nextActions: string[]
  recommendedTags: string[]
  relatedNoteIds: string[]
}
