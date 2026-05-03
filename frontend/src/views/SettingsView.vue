<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { NCard, NForm, NFormItem, NInput, NButton, NSelect, NText, NTag, NSpace, useMessage } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const message = useMessage()

const notionToken = ref('')
const notionDatabaseId = ref('')
const preferredLlm = ref('openai')
const customApiBase = ref('')
const customApiKey = ref('')
const customModelName = ref('')
const saving = ref(false)

onMounted(async () => {
  await authStore.loadSettings()
  notionDatabaseId.value = authStore.user.notionDefaultDatabaseId || ''
  preferredLlm.value = authStore.user.preferredLlm || 'openai'
  customApiBase.value = authStore.user.customLlmApiBase || ''
  customModelName.value = authStore.user.customLlmModelName || ''
})

const llmOptions = [
  { label: 'OpenAI (GPT-4o)', value: 'openai' },
  { label: 'Claude (Anthropic)', value: 'claude' },
  { label: 'Gemini (Google)', value: 'gemini' },
  { label: 'DeepSeek', value: 'deepseek' },
]

const showCustomConfig = computed(() => preferredLlm.value === 'deepseek')

async function handleSaveNotion() {
  saving.value = true
  try {
    await authStore.updateSettings({
      notion_access_token: notionToken.value || undefined,
      notion_default_database_id: notionDatabaseId.value || undefined,
    })
    message.success('Notion 配置已保存')
    notionToken.value = '' // Clear token from memory after save
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function handleSaveLlm() {
  saving.value = true
  try {
    await authStore.updateSettings({
      preferred_llm: preferredLlm.value,
      custom_llm_api_base: customApiBase.value || undefined,
      custom_llm_api_key: customApiKey.value || undefined,
      custom_llm_model_name: customModelName.value || undefined,
    })
    message.success('AI 配置已保存')
    customApiKey.value = '' // Clear key from memory after save
  } catch (error) {
    message.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="settings-view">
    <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 20px">设置</h2>

    <n-card title="Notion 集成" style="margin-bottom: 16px">
      <n-space align="center" style="margin-bottom: 12px">
        <n-text>状态：</n-text>
        <n-tag :type="authStore.user.notionConnected ? 'success' : 'warning'" round size="small">
          {{ authStore.user.notionConnected ? '已连接' : '未连接' }}
        </n-tag>
      </n-space>

      <n-form label-placement="left" label-width="160">
        <n-form-item label="集成 Token">
          <n-input
            v-model:value="notionToken"
            type="password"
            show-password-on="click"
            placeholder="ntn_xxxxxxxxxxxxx"
          />
        </n-form-item>
        <n-form-item label="默认数据库 ID">
          <n-input
            v-model:value="notionDatabaseId"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" size="small" @click="handleSaveNotion">保存并测试连接</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="AI 模型配置">
      <n-form label-placement="left" label-width="160">
        <n-form-item label="聊天模型">
          <n-select
            v-model:value="preferredLlm"
            :options="llmOptions"
            style="width: 300px"
          />
        </n-form-item>

        <template v-if="showCustomConfig">
          <n-form-item label="API 地址">
            <n-input
              v-model:value="customApiBase"
              placeholder="https://api.deepseek.com/v1"
            />
          </n-form-item>
          <n-form-item label="API 密钥">
            <n-input
              v-model:value="customApiKey"
              type="password"
              show-password-on="click"
              placeholder="sk-xxxxxxxxxxxxx"
            />
          </n-form-item>
          <n-form-item label="模型名称">
            <n-input
              v-model:value="customModelName"
              placeholder="deepseek-chat"
            />
          </n-form-item>
        </template>

        <n-form-item>
          <n-button type="primary" size="small" @click="handleSaveLlm">保存</n-button>
        </n-form-item>
      </n-form>

      <n-text depth="3" style="font-size: 12px">
        注：Embedding 模型固定使用 OpenAI text-embedding-3-small，以保证向量一致性。
      </n-text>
    </n-card>
  </div>
</template>

<style scoped>
.settings-view {
  max-width: 700px;
}
</style>
