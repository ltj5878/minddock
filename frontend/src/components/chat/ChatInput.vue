<script setup lang="ts">
import { ref } from 'vue'
import { NInput, NButton, NIcon } from 'naive-ui'
import { SendOutline } from '@vicons/ionicons5'

const emit = defineEmits<{
  send: [content: string]
}>()

const input = ref('')

function handleSend() {
  const content = input.value.trim()
  if (!content) return
  emit('send', content)
  input.value = ''
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="chat-input">
    <n-input
      v-model:value="input"
      type="textarea"
      placeholder="向你的知识库提问..."
      :autosize="{ minRows: 1, maxRows: 4 }"
      @keydown="handleKeydown"
      style="flex: 1"
    />
    <n-button
      type="primary"
      :disabled="!input.trim()"
      @click="handleSend"
      style="align-self: flex-end"
    >
      <template #icon>
        <n-icon><SendOutline /></n-icon>
      </template>
    </n-button>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  gap: 8px;
  padding: 16px;
  border-top: 1px solid var(--color-border);
  background: white;
}
</style>
