<template>
  <v-divider :thickness="2" color="black" />
  <v-row class="d-flex justify-center align-center pa-2 ga-3">
    <v-col cols="12" class="d-flex justify-start align-center">
      <h3>Test Result:</h3>
    </v-col>

    <template v-if="result.status === RES_STATUS.FAILED">
      <v-col>
        <v-alert type="error" dense text>{{ result.errorMessage }}</v-alert>
      </v-col>
    </template>

    <template v-else-if="result.status === RES_STATUS.SUCCESS">
      <v-col>
        <v-list>
          <v-list-item v-for="audioFile in result.audioFiles" :key="audioFile">
            <AudioPlayer
              :title="audioFile.split('/').at(-1).split('_')[0].toUpperCase()"
              :audioURL="audioFile"
            />
          </v-list-item>
        </v-list>
      </v-col>
      <v-col>
        <v-text-field v-model="result.logFile" label="Log File" readonly dense hide-details />
      </v-col>
    </template>
  </v-row>
</template>

<script setup>
import { RES_STATUS } from '../../constants/enums'
import AudioPlayer from '../AudioPlayer.vue'

defineProps({
  result: { type: Object, required: true },
})
</script>
