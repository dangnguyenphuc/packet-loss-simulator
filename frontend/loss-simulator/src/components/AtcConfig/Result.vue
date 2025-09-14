<template>
    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <!-- Failed -->
      <template v-if="result.status === RES_STATUS.FAILED">
        <v-col>
          <v-alert type="error" dense text>
            {{ result.errorMessage }}
          </v-alert>
        </v-col>
      </template>

      <!-- Success -->
      <template v-else-if="result.status === RES_STATUS.SUCCESS">
        <v-col cols="3">
          <v-select
            v-model="result.selectedAudio"
            :items="result.audioFiles"
            label="Audio Files"
            dense
            @update:model-value="onAudioChange"
            hide-details
          />
        </v-col>

        <!-- Play / Stop -->
        <v-col cols="2" class="d-flex align-center ga-2">
          <v-btn
            icon="mdi-play"
            color="primary"
            density="compact"
            @click="playAudio(result.selectedAudio)"
          />
          <v-btn
            icon="mdi-stop"
            color="red"
            density="compact"
            @click="stopAudio"
          />
        </v-col>

        <!-- Log file -->
        <v-col cols="4">
          <v-text-field
            v-model="result.logFile"
            label="Log File"
            readonly
            dense
            hide-details
          />
          <v-btn
            density="compact"
            prepend-icon="mdi-open-in-app"
            class="mt-1"
            @click="openLog(result.logFile)"
          >
            Open Log
          </v-btn>
        </v-col>
      </template>
    </v-row>
</template>

<script>
import { RES_STATUS } from "../../constants/enums";

export default {
  name: "Result",
  props: {
    result: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      RES_STATUS,
      audioInstance: null,
    };
  },
  methods: {
    playAudio(file) {
      if (!file) return;
      this.stopAudio();
      this.audioInstance = new Audio(file);
      this.audioInstance.play();
    },
    stopAudio() {
      if (this.audioInstance) {
        this.audioInstance.pause();
        this.audioInstance.currentTime = 0;
        this.audioInstance = null;
      }
    },
    onAudioChange(newFile) {
      this.stopAudio();
      console.log("Selected new audio file:", newFile);
    },
    openLog(file) {
      console.log("Opening log file:", file);
    },
  },
};
</script>
