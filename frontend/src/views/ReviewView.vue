<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NTabs, NTabPane, NCard, NText, NTimeline, NTimelineItem, NButton, NStatistic, NGrid, NGridItem } from 'naive-ui'
import { useNotesStore } from '../stores/notes'
import { useProjectsStore } from '../stores/projects'

const notesStore = useNotesStore()
const projectsStore = useProjectsStore()

const weeklyReviewText = ref('')
const generating = ref(false)

onMounted(async () => {
  if (!notesStore.loaded) await notesStore.loadNotes()
  if (!projectsStore.loaded) await projectsStore.loadProjects()
})

async function handleGenerateWeeklyReview() {
  generating.value = true
  try {
    weeklyReviewText.value = await notesStore.generateWeeklyReview()
  } catch (error) {
    console.error('Failed to generate review:', error)
  } finally {
    generating.value = false
  }
}

const todayNotes = computed(() => {
  const today = new Date().toDateString()
  return notesStore.notes.filter(
    (n) => new Date(n.createdAt).toDateString() === today
  )
})

const thisWeekNotes = computed(() => {
  const now = new Date()
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
  return notesStore.notes.filter((n) => new Date(n.createdAt) >= weekAgo)
})

const topThemes = computed(() => {
  const tagCount: Record<string, number> = {}
  thisWeekNotes.value.forEach((n: any) => {
    n.tags.forEach((t: string) => {
      tagCount[t] = (tagCount[t] || 0) + 1
    })
  })
  return Object.entries(tagCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([tag, count]) => ({ tag, count }))
})

const dailySummary = computed(() => `今天你向知识库新增了 ${todayNotes.value.length || '0'} 条笔记。

**关键观察：**
- 当前活跃项目数：**${projectsStore.activeProjects.length}**
- 当前待办任务数：**${projectsStore.pendingTasks.length}**
- 本周讨论最多的主题：${topThemes.value.map((t) => t.tag).join('、') || '暂无'}

**明天建议：**
1. 处理优先级最高的待办任务
2. 给活跃项目补充一条进展笔记
3. 回顾本周高频主题并沉淀为 next actions`)

const weeklySummaryHeuristic = computed(() => `## 每周复盘 (本地分析)

### 本周活动
- 知识库新增 **${thisWeekNotes.value.length} 条笔记**
- **${projectsStore.activeProjects.length} 个项目** 正在跟踪
- **${projectsStore.pendingTasks.length} 个任务** 待处理

### 主要主题
${topThemes.value.map((t: any) => `- **${t.tag}**（${t.count} 次提及）`).join('\n')}

### 建议
1. **补齐项目状态** — 确保每个活跃项目都有下一步动作
2. **清理低价值待办** — 删除或延后不再重要的任务
3. **沉淀高频主题** — 把本周反复出现的主题整理成结构化笔记`)
</script>

<template>
  <div class="review-view">
    <div class="review-header">
      <h2 style="font-size: 20px; font-weight: 600">复盘</h2>
      <n-button type="primary" size="small" :loading="generating" @click="handleGenerateWeeklyReview">生成 AI 每周总结</n-button>
    </div>

    <n-grid :cols="4" :x-gap="12" style="margin-bottom: 20px">
      <n-grid-item>
        <n-card size="small">
          <n-statistic label="本周笔记" :value="thisWeekNotes.length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small">
          <n-statistic label="活跃项目" :value="projectsStore.activeProjects.length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small">
          <n-statistic label="待办任务" :value="projectsStore.pendingTasks.length" />
        </n-card>
      </n-grid-item>
      <n-grid-item>
        <n-card size="small">
          <n-statistic label="热门主题" :value="topThemes.length" />
        </n-card>
      </n-grid-item>
    </n-grid>

    <n-tabs type="line" default-value="daily">
      <n-tab-pane name="daily" tab="每日复盘">
        <n-card style="margin-top: 12px">
          <template #header>
            <n-text strong>今日总结</n-text>
          </template>
          <div class="review-content" v-html="renderMarkdown(dailySummary)" />
        </n-card>

        <n-card v-if="todayNotes.length" style="margin-top: 12px">
          <template #header>
            <n-text strong>今日笔记</n-text>
          </template>
          <n-timeline>
            <n-timeline-item
              v-for="note in todayNotes"
              :key="note.id"
              :title="note.title"
              :content="note.summary"
              type="info"
            />
          </n-timeline>
          <n-text v-if="!todayNotes.length" depth="3">今天还没有新增笔记。</n-text>
        </n-card>
      </n-tab-pane>

      <n-tab-pane name="weekly" tab="每周复盘">
        <n-card style="margin-top: 12px">
          <div v-if="weeklyReviewText" class="review-content" v-html="renderMarkdown(weeklyReviewText)" />
          <div v-else-if="!generating" class="review-content" v-html="renderMarkdown(weeklySummaryHeuristic)" />
          <div v-else style="padding: 40px; text-align: center">
            <n-text depth="3">正在通过 AI 生成深度复盘报告...</n-text>
          </div>
        </n-card>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<script lang="ts">
import MarkdownIt from 'markdown-it'
const md = new MarkdownIt()
function renderMarkdown(content: string): string {
  return md.render(content)
}
</script>

<style scoped>
.review-view {
  max-width: 900px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.review-content {
  line-height: 1.7;
  font-size: 14px;
}

.review-content :deep(h2) {
  font-size: 1.2em;
  margin-top: 16px;
  margin-bottom: 8px;
}

.review-content :deep(h3) {
  font-size: 1.05em;
  margin-top: 12px;
  margin-bottom: 6px;
}

.review-content :deep(ul) {
  padding-left: 20px;
}

.review-content :deep(li) {
  margin-bottom: 4px;
}

.review-content :deep(strong) {
  font-weight: 600;
}

.review-content :deep(ol) {
  padding-left: 20px;
}
</style>
