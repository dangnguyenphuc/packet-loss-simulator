<template>
  <v-container>
    <v-row class="d-flex flex-column justify-center align-start ga-3">
      <v-checkbox v-model="enableAutoStop" label="Auto Stop" />
      <v-btn density="compact" color="black" prepend-icon="mdi-record-circle" @click="startCaptureAll" :disabled="isStartCaptureAll">Start Capture All</v-btn>
      <v-btn density="compact" color="red"   prepend-icon="mdi-pause-circle"  @click="stopCaptureAll">Stop Capture All</v-btn>
      <v-btn density="compact" color="green" prepend-icon="mdi-reload"        @click="resetAll">Reset All</v-btn>
    </v-row>
    <v-row>
      <v-col v-for="(graph, index) in graphs" :key="index" cols="6" md="12">
        <LineGraph
          :graphTitle="graph.title"
          :series="graph.series"
          @[EVENT_START_MONITORING]="startCapture"
          @[EVENT_STOP_MONITORING]="stopCapture"
          @[EVENT_RESET_MONITORING]="resetMonitor"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onBeforeUnmount } from 'vue'
import LineGraph from './LineGraph.vue'
import {
  EVENT_START_MONITORING, EVENT_STOP_MONITORING, EVENT_RESET_MONITORING,
  BENCHMARK_DURATION, RETRY_DELAY,
} from '../../constants/constant'
import { getStat } from '../../utils/specific'

const props = defineProps({
  deviceId: { type: String, required: true },
})

const isStartCaptureAll = ref(false)
const enableAutoStop    = ref(true)
let autoStopTimer = null

const graphs = ref([
  { title: 'mem', series: [{ name: 'Used memory MB', data: [] }], timer: null },
  { title: 'cpu', series: [{ name: 'Used CPU %',    data: [] }], timer: null },
])

async function startCaptureAll() {
  try {
    await getStat({ type: 'start', id: props.deviceId })
  } catch { /* non-critical */ }

  clearTimeout(autoStopTimer)
  for (const graph of graphs.value) await startCapture(graph.title)
  isStartCaptureAll.value = true

  if (enableAutoStop.value) {
    autoStopTimer = setTimeout(stopCaptureAll, BENCHMARK_DURATION)
  }
}

async function stopCaptureAll() {
  for (const graph of graphs.value) stopCapture(graph.title)
  isStartCaptureAll.value = false
  try {
    await getStat({ type: 'stop', id: props.deviceId })
  } catch { /* non-critical */ }
}

function resetAll() {
  for (const graph of graphs.value) resetMonitor(graph.title)
  isStartCaptureAll.value = false
}

async function startCapture(type) {
  const graph = graphs.value.find(g => g.title === type)
  if (!graph || graph.timer) return

  graph.timer = setInterval(async () => {
    try {
      const res = await getStat({ type, id: props.deviceId })
      if (!res || !Object.hasOwn(res, 'data') || res.data < 0) return
      const series = graph.series[0].data
      series.push(res.data)
      graph.series = [{ ...graph.series[0], data: [...series] }]
    } catch { /* ignore */ }
  }, RETRY_DELAY)
}

function stopCapture(type) {
  const graph = graphs.value.find(g => g.title === type)
  if (!graph?.timer) return
  clearInterval(graph.timer)
  graph.timer = null
}

function resetMonitor(type) {
  const graph = graphs.value.find(g => g.title === type)
  if (!graph) return
  clearInterval(graph.timer)
  graph.timer = null
  graph.series = [{ ...graph.series[0], data: [] }]
}

onBeforeUnmount(() => {
  graphs.value.forEach(g => { if (g.timer) clearInterval(g.timer) })
  clearTimeout(autoStopTimer)
})
</script>
