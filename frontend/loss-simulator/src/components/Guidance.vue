<template>
  <div>
    <pre>{{ content }}</pre>
  </div>
  <div class="mt-5 d-flex flex-row justify-center align-center ga-2">
    <v-btn
      :disabled="!deviceId"
      :color="status === TEST_STATUS.FAIL ? 'red' : 'green'"
      @click="startInstall"
    >
      <template #prepend>
        <v-progress-circular v-if="status === TEST_STATUS.TESTING" indeterminate size="18" width="2" />
        <v-icon v-else>{{ statusIcon }}</v-icon>
      </template>
      <span>{{ status === TEST_STATUS.TESTING ? 'Stop' : 'Install' }}</span>
    </v-btn>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { EVENT_OPEN_TOAST } from '../constants/constant'
import { TEST_STATUS } from '../constants/enums'
import { installApp, stopApp } from '../utils/specific'

const props = defineProps({
  content:  { type: String },
  deviceId: { type: String },
})

const emit = defineEmits([EVENT_OPEN_TOAST])

const status = ref(TEST_STATUS.PENDING)
const taskId = ref('')

const statusIcon = computed(() => {
  if (status.value === TEST_STATUS.PASS) return 'mdi-check-circle'
  if (status.value === TEST_STATUS.FAIL) return 'mdi-close-circle'
  return 'mdi-play-circle'
})

async function startInstall() {
  if (status.value === TEST_STATUS.TESTING) {
    status.value = TEST_STATUS.PENDING
    try { await stopApp(taskId.value) } catch { /* best-effort */ }
    taskId.value = ''
    return
  }

  status.value = TEST_STATUS.TESTING
  try {
    const result = await installApp(props.deviceId)
    taskId.value = result.taskId
    try { await stopApp(taskId.value) } catch { /* best-effort */ }
    taskId.value = ''
    status.value = TEST_STATUS.PASS
  } catch (e) {
    emit(EVENT_OPEN_TOAST, e.message)
    status.value = TEST_STATUS.FAIL
  }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  text-align: left;
}
</style>
