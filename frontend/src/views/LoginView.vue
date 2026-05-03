<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NCard, NForm, NFormItem, NInput, NButton, NText } from 'naive-ui'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

function handleLogin() {
  authStore.login(email.value, password.value)
  router.push('/inbox')
}
</script>

<template>
  <div class="login-view">
    <n-card style="width: 400px">
      <template #header>
        <div style="text-align: center">
          <span style="font-size: 36px">🧠</span>
          <h2 style="font-size: 22px; font-weight: 600; margin-top: 8px">MindDock</h2>
          <n-text depth="3">你的 AI 知识工作台</n-text>
        </div>
      </template>

      <n-form>
        <n-form-item label="邮箱">
          <n-input v-model:value="email" placeholder="you@example.com" />
        </n-form-item>
        <n-form-item label="密码">
          <n-input v-model:value="password" type="password" show-password-on="click" placeholder="请输入密码" />
        </n-form-item>
        <n-button type="primary" block @click="handleLogin">登录</n-button>
      </n-form>

      <template #footer>
        <n-text depth="3" style="font-size: 13px; text-align: center; display: block">
          还没有账号？<a href="#">注册</a>
        </n-text>
      </template>
    </n-card>
  </div>
</template>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: var(--color-bg);
}
</style>
