<template>
  <div class="text-center">
    <v-snackbar
      v-model="snackbar"
      :timeout="timeout"
    >
      <div class="text-subtitle-1 pb-2">{{ header }}</div>
      <p>{{ message }}</p>

      <template v-slot:actions>
        <v-btn
            color="red"
            density="compact"
            icon="mdi-close"
            @click="close"
        >
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script>
import { EVENT_CLOSE_TOAST } from '../constants/constant'

export default {
  name: "Toast",
  props: {
    isOpen: {
      type: Boolean,
      required: true,
    },
    timeout: {
      type: Number,
      default: 3000,
    },
    header: {
        type: String,
        required: false,
        default: "Header"
    },
    message: {
        type: String,
        required: false,
        default: "Message"
    }
  },
  data() {
    return {
      snackbar: this.isOpen,
    }
  },
  watch: {
    isOpen(newVal) 
    {
        this.snackbar = newVal
    },
    snackbar(newVal) 
    {
        if (!newVal)
            this.close()
    }
    
  },
  methods: {
    close() {
      this.$emit(EVENT_CLOSE_TOAST)
    },
  },
}
</script>
