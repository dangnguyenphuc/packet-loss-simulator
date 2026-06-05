<template>
  <div class="test-info-container">
    <v-row class="pa-4 d-flex flex-auto ga-2" align="center" justify="center">
      <v-col class="d-flex ga-2 flex-column">
        <v-row class="d-flex justify-center align-center">
          <span>PC Info</span>
        </v-row>
        <v-row
          v-for="field in infoFieldsPC" :key="field.title"
          class="d-flex info-pc-row justify-center align-center rounded-pill pa-4"
        >
          <v-col class="justify-center align-center">
            <v-row class="d-flex justify-center align-center">
              <span>{{ field.title }}</span>
            </v-row>
            <v-row class="d-flex flex-column gap-2">
              <template v-if="Array.isArray(field.data) && field.data.length > 0">
                <template v-if="field.title !== 'Audio Files'">
                  <v-text-field
                    v-for="(d, i) in field.data" :key="i"
                    :model-value="d" readonly density="compact"
                  />
                </template>
                <template v-else>
                  <v-row v-for="(d, i) in field.data" :key="i">
                    <v-col cols="8">
                      <v-text-field :model-value="extractFilename(d)" label="File" readonly density="compact" />
                    </v-col>
                    <v-col cols="4">
                      <v-text-field :model-value="extractDuration(d)" label="Duration" readonly density="compact" />
                    </v-col>
                  </v-row>
                </template>
              </template>
              <template v-else>
                <v-text-field :model-value="field.data" readonly density="compact" />
              </template>
            </v-row>
          </v-col>
        </v-row>
      </v-col>

      <v-col class="d-flex flex-column ga-2">
        <v-row class="d-flex justify-center align-center">
          <span>Android Info</span>
        </v-row>
        <v-row
          v-for="field in infoFieldsAndroid" :key="field.title"
          class="d-flex info-row justify-center align-center rounded-pill pa-4"
        >
          <v-col class="justify-center align-center">
            <v-row class="d-flex justify-center align-center">
              <span>{{ field.title }}</span>
            </v-row>
            <v-row class="d-flex flex-column gap-2">
              <template v-if="Array.isArray(field.data) && field.data.length > 0">
                <v-text-field v-for="(d, i) in field.data" :key="i" :model-value="d" readonly density="compact" />
              </template>
              <template v-else>
                <v-text-field :model-value="field.data" readonly density="compact" />
              </template>
            </v-row>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { fetchInfo } from '../utils/specific'
import { EVENT_OPEN_TOAST } from '../constants/constant'

const props = defineProps({
  deviceId: { type: String, default: '' },
})

const emit = defineEmits([EVENT_OPEN_TOAST])

const emptyPC = () => [
  { title: 'Audio Files', data: [] },
  { title: 'Record Folder', data: '' },
]

const emptyAndroid = () => [
  { title: 'Uploaded Audio Folder', data: '' },
  { title: 'Record Audio Folder', data: '' },
  { title: 'Histogram Folder', data: '' },
  { title: 'App Package', data: '' },
  { title: 'Target Activities', data: [] },
]

const infoFieldsPC      = ref(emptyPC())
const infoFieldsAndroid = ref(emptyAndroid())

function extractFilename(path) {
  if (!path) return ''
  return path.substring(0, path.lastIndexOf('-'))
}

function extractDuration(path) {
  if (!path) return ''
  return path.substring(path.lastIndexOf('-') + 1)
}

async function fetchTestInfo() {
  if (!props.deviceId) return
  try {
    const info = await fetchInfo(props.deviceId)
    infoFieldsPC.value[0].data = info.pc.audio
    infoFieldsPC.value[1].data = info.pc.recordFolder
    infoFieldsAndroid.value[0].data = info.android.uploadAudioFolder
    infoFieldsAndroid.value[1].data = info.android.recordAudioFolder
    infoFieldsAndroid.value[2].data = info.android.histogramStorePath
    infoFieldsAndroid.value[3].data = info.android.appPackage
    infoFieldsAndroid.value[4].data = info.android.activity
  } catch (err) {
    emit(EVENT_OPEN_TOAST, 'TestInfo', 'Get Info error', err.message)
  }
}

watch(() => props.deviceId, newVal => {
  if (!newVal) {
    infoFieldsPC.value      = emptyPC()
    infoFieldsAndroid.value = emptyAndroid()
  }
  fetchTestInfo()
})

onMounted(fetchTestInfo)
</script>

<style scoped>
.info-row {
  background-color: rgb(227, 198, 255);
}
.info-pc-row {
  background-color: rgb(238, 223, 232);
}
</style>
