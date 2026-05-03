import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '../api/client'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(true)
  const user = ref({
    id: 'mock-user-1',
    email: 'demo@minddock.app',
    preferredLlm: 'openai',
    notionConnected: false,
    notionDefaultDatabaseId: '',
    customLlmApiBase: '',
    customLlmModelName: '',
  })

  async function loadSettings() {
    try {
      const resp = await client.get('/settings')
      const data = resp.data
      user.value.email = data.email
      user.value.preferredLlm = data.preferred_llm
      user.value.notionConnected = data.notion_connected
      user.value.notionDefaultDatabaseId = data.notion_default_database_id
      user.value.customLlmApiBase = data.custom_llm_api_base
      user.value.customLlmModelName = data.custom_llm_model_name
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  async function updateSettings(settings: any) {
    try {
      const resp = await client.patch('/settings', settings)
      const data = resp.data
      user.value.preferredLlm = data.preferred_llm
      user.value.notionConnected = data.notion_connected
      user.value.notionDefaultDatabaseId = data.notion_default_database_id
      user.value.customLlmApiBase = data.custom_llm_api_base
      user.value.customLlmModelName = data.custom_llm_model_name
      return data
    } catch (error) {
      console.error('Failed to update settings:', error)
      throw error
    }
  }

  function login(email: string, _password: string) {
    user.value.email = email
    isLoggedIn.value = true
  }

  function logout() {
    isLoggedIn.value = false
    localStorage.removeItem('access_token')
  }

  return { isLoggedIn, user, login, logout, loadSettings, updateSettings }
})
