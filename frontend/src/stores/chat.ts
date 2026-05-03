import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage, Citation } from '../types'
import client from '../api/client'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  async function sendMessage(content: string) {
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      createdAt: new Date().toISOString(),
    }
    messages.value.push(userMsg)
    loading.value = true

    try {
      const { data } = await client.post<{
        answer: string
        citations: Array<{
          note_id: string
          note_title: string
          chunk_text: string
          similarity: number
        }>
        model_used: string
      }>('/chat/ask', { question: content })

      const aiMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: data.answer,
        citations: data.citations.map(
          (citation): Citation => ({
            noteId: citation.note_id,
            noteTitle: citation.note_title,
            chunkText: citation.chunk_text,
            similarity: citation.similarity,
          })
        ),
        createdAt: new Date().toISOString(),
      }
      messages.value.push(aiMsg)
    } catch (error) {
      const aiMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        role: 'assistant',
        content: `本地问答接口暂时不可用：${error instanceof Error ? error.message : 'unknown error'}`,
        createdAt: new Date().toISOString(),
      }
      messages.value.push(aiMsg)
    } finally {
      loading.value = false
    }
  }

  function clearMessages() {
    messages.value = []
  }

  return { messages, loading, sendMessage, clearMessages }
})
