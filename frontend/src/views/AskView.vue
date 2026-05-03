<script setup lang="ts">
import { useChatStore } from '../stores/chat'
import ChatWindow from '../components/chat/ChatWindow.vue'
import ChatInput from '../components/chat/ChatInput.vue'

const chatStore = useChatStore()

function handleSend(content: string) {
  chatStore.sendMessage(content)
}
</script>

<template>
  <div class="ask-view">
    <div class="ask-header">
      <h2 style="font-size: 20px; font-weight: 600">知识问答</h2>
    </div>
    <div class="chat-container">
      <ChatWindow />
      <ChatInput @send="handleSend" />
    </div>
  </div>
</template>

<style scoped>
.ask-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.ask-header {
  margin-bottom: 16px;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  min-height: 0;
  overflow: hidden;
}
</style>
