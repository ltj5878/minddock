<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { NScrollbar, NSpin, NEmpty, NText } from 'naive-ui'
import { useChatStore } from '../../stores/chat'
import ChatMessage from './ChatMessage.vue'

const chatStore = useChatStore()
const scrollRef = ref<InstanceType<typeof NScrollbar> | null>(null)

watch(
  () => chatStore.messages.length,
  async () => {
    await nextTick()
    scrollRef.value?.scrollTo({ top: 99999, behavior: 'smooth' })
  }
)
</script>

<template>
  <div class="chat-window">
    <n-scrollbar ref="scrollRef" style="flex: 1; padding: 16px">
      <n-empty
        v-if="!chatStore.messages.length"
        description="向你的知识库提问"
        style="margin-top: 40%"
      >
        <template #extra>
          <n-text depth="3" style="font-size: 13px">
            试试："我关于 AI 工作台的想法有哪些？" 或 "帮我总结最近的笔记"
          </n-text>
        </template>
      </n-empty>

      <ChatMessage
        v-for="msg in chatStore.messages"
        :key="msg.id"
        :message="msg"
      />

      <div v-if="chatStore.loading" class="loading-indicator">
        <n-spin size="small" />
        <n-text depth="3" style="font-size: 13px; margin-left: 8px">
          正在搜索你的知识库...
        </n-text>
      </div>
    </n-scrollbar>
  </div>
</template>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.loading-indicator {
  display: flex;
  align-items: center;
  padding: 8px 0;
}
</style>
