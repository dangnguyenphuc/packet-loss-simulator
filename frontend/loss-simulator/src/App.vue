<template>
  <v-app>
    <router-view @open:Toast="showToast"></router-view>

    <Toast 
      :isOpen="toastOpen" 
      :header="toastHeader"
      :message="toastMessage"
      :timeout="toastTimeout" 
      @close:Toast="closeToast" 
    />
  </v-app>
</template>

<script>
import Toast from './components/Toast.vue'
import { TOAST_TIMEOUT } from './constants/constant'

export default {
  name: 'App',
  components: { Toast },
  data() {
    return {
      toastOpen: false,
      toastHeader: "",
      toastMessage: "",
      toastTimeout: TOAST_TIMEOUT,
    }
  },
  methods: {
    showToast(header = "", msg = "", timeout = TOAST_TIMEOUT) {
      this.toastHeader = header;
      this.toastMessage = msg;
      this.toastTimeout = timeout;
      this.toastOpen = true;
    },
    closeToast()
    {
      this.toastOpen = false;
    }
  }
}
</script>
