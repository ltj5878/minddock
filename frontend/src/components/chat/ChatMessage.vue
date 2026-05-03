<script setup lang="ts">
import { NText, NSpace } from 'naive-ui'
import type { ChatMessage } from '../../types'
import MarkdownRenderer from '../common/MarkdownRenderer.vue'
import CitationCard from './CitationCard.vue'

defineProps<{
  message: ChatMessage
}>()

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="chat-message" :class="message.role">
    <div class="message-bubble">
      <MarkdownRenderer v-if="message.role === 'assistant'" :content="message.content" />
      <n-text v-else style="white-space: pre-wrap">{{ message.content }}</n-text>

      <div v-if="message.citations?.length" class="citations">
        <n-text depth="3" style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; display: block">
          引用来源
        </n-text>
        <n-space vertical :size="6">
          <CitationCard
            v-for="(c, i) in message.citations"
            :key="c.noteId"
            :citation="c"
            :index="i + 1"
          />
        </n-space>
      </div>
    </div>
    <n-text depth="3" style="font-size: 11px; margin-top: 4px">
      {{ formatTime(message.createdAt) }}
    </n-text>
  </div>
</template>

<style scoped>
.chat-message {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

.chat-message.user {
  align-items: flex-end;
}

.chat-message.assistant {
  align-items: flex-start;
}

.message-bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: var(--radius-md);
}

.user .message-bubble {
  background: var(--color-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .message-bubble {
  background: white;
  border: 1px solid var(--color-border);
  border-bottom-left-radius: 4px;
}

.citations {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border);
}
</style>
