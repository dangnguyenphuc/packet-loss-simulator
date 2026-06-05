<template>
  <div class="text-center">
    <v-snackbar v-model="snackbar" :timeout="timeout">
      <div class="text-subtitle-1 pb-2">{{ header }}</div>
      <p>{{ message }}</p>
      <template #actions>
        <v-btn color="red" density="compact" icon="mdi-close" @click="close" />
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { EVENT_CLOSE_TOAST } from '../constants/constant'

const props = defineProps({
  isOpen:  { type: Boolean, required: true },
  timeout: { type: Number, default: 3000 },
  header:  { type: String, default: 'Header' },
  message: { type: String, default: 'Message' },
})

const emit = defineEmits([EVENT_CLOSE_TOAST])

const snackbar = ref(props.isOpen)

watch(() => props.isOpen, val => { snackbar.value = val })
watch(snackbar, val => { if (!val) close() })

function close() {
  emit(EVENT_CLOSE_TOAST)
}
</script>
