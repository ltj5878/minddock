<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent } from 'naive-ui'
import AppSidebar from '../components/layout/AppSidebar.vue'
import ContextPanel from '../components/layout/ContextPanel.vue'
import { useUiStore } from '../stores/ui'

const ui = useUiStore()
</script>

<template>
  <n-layout has-sider style="height: 100%">
    <n-layout-sider
      bordered
      :width="ui.sidebarCollapsed ? 64 : 240"
      :collapsed="ui.sidebarCollapsed"
      collapse-mode="width"
      :collapsed-width="64"
      show-trigger
      @collapse="ui.sidebarCollapsed = true"
      @expand="ui.sidebarCollapsed = false"
      :native-scrollbar="false"
      style="background: #fff"
    >
      <AppSidebar />
    </n-layout-sider>

    <n-layout>
      <n-layout has-sider sider-placement="right" style="height: 100%">
        <n-layout-content :native-scrollbar="false" style="padding: 24px">
          <router-view />
        </n-layout-content>

        <n-layout-sider
          v-if="ui.contextPanelOpen"
          bordered
          :width="320"
          :native-scrollbar="false"
          style="background: #fff"
        >
          <ContextPanel />
        </n-layout-sider>
      </n-layout>
    </n-layout>
  </n-layout>
</template>
