<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NMenu, NIcon, NSpace, NText } from 'naive-ui'
import type { MenuOption } from 'naive-ui'
import {
  MailOutline,
  ChatbubblesOutline,
  FolderOpenOutline,
  CalendarOutline,
  SettingsOutline,
} from '@vicons/ionicons5'

const router = useRouter()
const route = useRoute()

function renderIcon(icon: any) {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions: MenuOption[] = [
  {
    label: '收集箱',
    key: 'inbox',
    icon: renderIcon(MailOutline),
  },
  {
    label: '知识问答',
    key: 'ask',
    icon: renderIcon(ChatbubblesOutline),
  },
  {
    label: '项目',
    key: 'projects',
    icon: renderIcon(FolderOpenOutline),
  },
  {
    label: '复盘',
    key: 'review',
    icon: renderIcon(CalendarOutline),
  },
  {
    type: 'divider',
    key: 'd1',
  },
  {
    label: '设置',
    key: 'settings',
    icon: renderIcon(SettingsOutline),
  },
]

const activeKey = computed(() => {
  const name = route.name as string
  if (name === 'ProjectDetail') return 'projects'
  return name?.toLowerCase() || 'inbox'
})

function handleMenuUpdate(key: string) {
  router.push(`/${key}`)
}
</script>

<template>
  <div class="sidebar-container">
    <div class="sidebar-logo">
      <n-space align="center" :size="8">
        <span class="logo-icon">🧠</span>
        <n-text strong style="font-size: 18px">MindDock</n-text>
      </n-space>
    </div>
    <n-menu
      :options="menuOptions"
      :value="activeKey"
      @update:value="handleMenuUpdate"
      :indent="20"
    />
  </div>
</template>

<style scoped>
.sidebar-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-logo {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--color-border);
}

.logo-icon {
  font-size: 24px;
}
</style>
