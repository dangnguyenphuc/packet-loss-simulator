<template>
  <v-app>
    <router-view @open:Toast="showToast" />
    <Toast
      :isOpen="toastOpen"
      :header="toastHeader"
      :message="toastMessage"
      :timeout="toastTimeout"
      @close:Toast="closeToast"
    />
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import Toast from './components/Toast.vue'
import { TOAST_TIMEOUT } from './constants/constant'

const toastOpen    = ref(false)
const toastHeader  = ref('')
const toastMessage = ref('')
const toastTimeout = ref(TOAST_TIMEOUT)

function showToast(header = '', msg = '', timeout = TOAST_TIMEOUT) {
  toastHeader.value  = header
  toastMessage.value = msg
  toastTimeout.value = timeout
  toastOpen.value    = true
}

function closeToast() {
  toastOpen.value = false
}
</script>
