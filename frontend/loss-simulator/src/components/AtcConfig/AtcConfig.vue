<template>
  <v-container class="d-flex flex-column ga-3">
    <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0 ga-3">
      <v-col cols="1" class="d-flex justify-center align-center">
        <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact" :disabled="!!result" />
      </v-col>
      <v-col class="d-flex flex-column justify-start align-start ga-2">
        <v-row class="d-flex justify-center align-center ga-2">
          <span>Atc Config</span>
          <v-select
            v-model="row.select"
            :items="selectorOptions"
            hide-details
            @update:modelValue="onConfigSelected(row, $event)"
          />
        </v-row>
        <v-row class="d-flex">
          <Timer
            :hour="row.timer.h"
            :minute="row.timer.m"
            :second="row.timer.s"
            @update:hour="val => row.timer.h = val"
            @update:minute="val => row.timer.m = val"
            @update:second="val => row.timer.s = val"
          />
        </v-row>
      </v-col>
      <v-col v-if="row.select" cols="6" md="7" xs="12">
        <Editor v-model="row.jsonData" />
      </v-col>
    </v-row>

    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" icon="mdi-plus" @click="addRow" />
      <v-btn density="compact" icon="mdi-restart" @click="resetRows" />
    </v-row>
    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" color="red" prepend-icon="mdi-stop-circle" @click="emit(EVENT_STOP_APP)" :disabled="taskId.length <= 0">Stop</v-btn>
      <v-btn density="compact" color="green" prepend-icon="mdi-play-circle" @click="emit(EVENT_START_APP)" :disabled="taskId !== '' && !result">Run Test</v-btn>
    </v-row>
    <v-row>
      <Result v-if="result" :result="result" />
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Editor from '../Editor.vue'
import Timer from '../Timer.vue'
import Result from './Result.vue'
import { fetchJsonContent } from '../../utils/specific'
import {
  EVENT_OPEN_TOAST, EVENT_UPDATE_MODEL, DEFAULT_ATC_TIMEOUT,
  EVENT_STOP_APP, EVENT_START_APP,
} from '../../constants/constant'

const props = defineProps({
  modelValue:    { required: true },
  definedConfig: { default: () => [] },
  result:        { required: true },
  taskId:        { required: true },
})

const emit = defineEmits([EVENT_UPDATE_MODEL, EVENT_OPEN_TOAST, EVENT_STOP_APP, EVENT_START_APP])

const rows = ref(props.modelValue)

const selectorOptions = computed(() =>
  props.definedConfig.map(path => path.split('/').pop())
)

watch(rows, newValue => emit(EVENT_UPDATE_MODEL, newValue), { deep: true })

watch(() => props.modelValue, newValue => {
  if (newValue !== rows.value) rows.value = newValue
})

function addRow() {
  rows.value.push({
    id: Date.now(),
    select: null,
    jsonData: '',
    timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT / 1000 },
  })
}

function deleteRow(index) {
  rows.value.splice(index, 1)
}

function resetRows() {
  rows.value = []
  addRow()
}

async function onConfigSelected(row, value) {
  try {
    const res = await fetchJsonContent(value)
    if (!res?.data) throw new Error(`Missing field when fetching: ${value}`)
    row.jsonData = JSON.stringify(res.data, null, 2)
  } catch (err) {
    emit(EVENT_OPEN_TOAST, 'AtcConfig', 'Error Getting JSON file', err.message)
  }
}
</script>
