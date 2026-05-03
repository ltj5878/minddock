<script setup lang="ts">
import { NTag } from 'naive-ui'

defineProps<{
  tag: string
  closable?: boolean
}>()

defineEmits<{
  close: []
}>()
</script>

<template>
  <n-tag
    size="small"
    :bordered="false"
    round
    :closable="closable"
    @close="$emit('close')"
    style="margin-right: 4px; margin-bottom: 4px"
  >
    {{ tag }}
  </n-tag>
</template>
