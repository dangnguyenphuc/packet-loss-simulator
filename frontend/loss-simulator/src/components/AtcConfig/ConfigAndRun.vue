<template>
  <v-container class="d-flex flex-column ga-3">
    <!-- Input -->
    <v-row>
      <v-col class="d-flex justify-center align-center">
        <v-text-field v-model="numTests" type="text" label="Number of Tests" hide-details />
      </v-col>
      <v-col class="d-flex justify-center align-center">
        <v-btn prepend-icon="$vuetify" @click="validateNumTests">Generate Test</v-btn>
      </v-col>
      <v-col class="d-flex justify-center align-center">
        <v-checkbox v-model="pullAudio" label="Pull Record Audio" hide-details />
      </v-col>
    </v-row>

    <!-- Panels -->
    <v-row>
      <v-expansion-panels v-model="expanded" multiple>
        <v-expansion-panel v-for="(test, index) in configs" :key="test.id" :value="index">
          <v-expansion-panel-title>
            <v-row class="w-100 d-flex align-center">
              <v-col>Test #{{ index + 1 }}</v-col>
              <v-col class="d-flex justify-end align-center ga-2">
                <v-btn @click.stop="deleteTest(index)" color="red" icon="mdi-delete" density="compact" />
                <v-progress-circular v-if="test.status === TEST_STATUS.TESTING" indeterminate color="primary" size="20" width="2" />
                <v-icon v-else-if="test.status === TEST_STATUS.PASS" color="green">mdi-check-circle</v-icon>
                <v-icon v-else-if="test.status === TEST_STATUS.FAIL" color="red">mdi-close-circle</v-icon>
                <v-icon v-else-if="test.status === TEST_STATUS.PENDING" color="grey">mdi-help-circle</v-icon>
              </v-col>
            </v-row>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <div class="d-flex justify-center align-center">
              <v-col>
                <v-checkbox v-model="test.enableOpusPlc" label="Enable Opus PLC" class="d-flex align-center justify-start" />
              </v-col>
              <v-col class="d-flex justify-center align-center ga-3">
                <span>Enc Complex</span>
                <v-select v-model="test.complexity" style="max-width: 100px" density="compact" :items="complexityOptions" hide-details />
              </v-col>
              <v-col class="d-flex justify-center align-center ga-3">
                <span>Dec Complex</span>
                <v-select v-model="test.decComplexity" style="max-width: 100px" density="compact" :items="complexityOptions" hide-details />
              </v-col>
              <v-col class="justify-center align-center ga-3">
                <span>DRED Duration</span>
                <div class="d-flex justify-center align-center">
                  <div style="width: 120px">
                    <v-text-field v-model.number="test.dredDuration" type="number" density="compact" clearable />
                  </div>
                </div>
              </v-col>
            </div>
            <AtcConfig
              @open:Toast="openToast"
              @stop:AndroidApp="() => stopAndroidApp(index)"
              @start:AndroidApp="() => startAndroidApp(index)"
              v-model="test.atcConfigs"
              :taskId="test.taskId"
              :result="test.result"
              :definedConfig="atcConfigs"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>

    <!-- Controls -->
    <v-row class="pa-0">
      <v-col class="d-flex flex-row justify-start align-center ga-3">
        <v-btn color="green" variant="tonal" @click="addTest">Add Test</v-btn>
      </v-col>
      <v-col class="d-flex flex-row justify-end align-center ga-3">
        <v-btn color="primary" @click="runTests" :disabled="configs.length === 0">Run All Tests</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { TEST_STATUS, RES_STATUS } from '../../constants/enums'
import {
  DEFAULT_ATC_TIMEOUT, EVENT_OPEN_TOAST, TOAST_TIMEOUT,
  MAX_RETRIES, RETRY_DELAY, EVAL_COMPLEX, EVAL_LOSS_PERCENTAGE,
  EVAL_NORMAL_AND_PLC, EVAL_NETWORK_TYPE, EVAL_DEC_COMPLEX,
  EVAL_DRED, MAX_CONFIG_SIZE, EVAL_RTT,
  EVAL_SUBCASE_LOSS, EVAL_SUBCASE_DELAY,
} from '../../constants/constant'
import AtcConfig from './AtcConfig.vue'
import Result from './Result.vue'
import { applyConfig, deleteShape, runApp, getAppRes, stopApp, removeFolder, moveAudios } from '../../utils/specific'
import { DEFAULT_REQUEST_TIMEOUT } from '../../constants/api'

const props = defineProps({
  atcConfigs: { default: () => [] },
  deviceId:   { required: true, type: String },
  deviceIp:   { required: true, type: String },
})

const emit = defineEmits([EVENT_OPEN_TOAST])

const numTests        = ref('0')
const pullAudio       = ref(false)
const configs         = ref([])
const configsBuffer   = ref([])
const expanded        = ref([])
const complexityOptions = Array.from({ length: 10 }, (_, i) => i + 1)

// ── helpers ──────────────────────────────────────────────────────────────────

function createTest(i = 0) {
  return {
    id: Date.now() + i,
    status: TEST_STATUS.PENDING,
    atcConfigs: [{
      id: `${Date.now()}_${i}`,
      select: '',
      jsonData: '',
      timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT / 1000 },
    }],
    complexity: 5,
    decComplexity: 6,
    dredDuration: 10,
    taskId: '',
    cancelled: false,
    enableOpusPlc: false,
    result: null,
  }
}

function createTestPlc(index, decComplexity, usePlc, networkType, jsonString) {
  return {
    id: `${Date.now()}${decComplexity}_${usePlc}_${index}`,
    status: TEST_STATUS.PENDING,
    atcConfigs: [{
      id: `${Date.now()}_${decComplexity}_${usePlc}_${index}`,
      select: networkType,
      jsonData: jsonString,
      timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT / 1000 },
    }],
    decComplexity,
    taskId: '',
    cancelled: false,
    enableOpusPlc: usePlc,
    result: null,
  }
}

function createTestDred(index, complexity, decComplexity, dredDuration, networkType, jsonString) {
  return {
    id: `${Date.now()}${complexity}_${decComplexity}_${dredDuration}_${index}`,
    status: TEST_STATUS.PENDING,
    atcConfigs: [{
      id: `${Date.now()}_${complexity}_${decComplexity}_${dredDuration}_${index}`,
      select: networkType,
      jsonData: jsonString,
      timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT / 1000 },
    }],
    complexity,
    decComplexity,
    dredDuration,
    taskId: '',
    cancelled: false,
    enableOpusPlc: false,
    result: null,
  }
}

// ── generation ────────────────────────────────────────────────────────────────

function validateNumTests() {
  const trimmed = numTests.value.trim()
  if (trimmed === 'plc') {
    generateSampleConfigsForPlc()
  } else if (trimmed === 'dred') {
    generateSampleConfigsForDred()
  } else if (trimmed === 'full') {
    generateFullSweepConfigs()
  } else {
    const value = Math.max(0, parseInt(trimmed, 10) || 0)
    numTests.value = String(value)
    generateConfigs()
  }
}

function generateConfigs() {
  configs.value = Array.from({ length: parseInt(numTests.value) }, (_, i) => createTest(i))
  expanded.value = configs.value.map((_, i) => i)
}

function generateSampleConfigsForPlc() {
  configs.value = []
  configsBuffer.value = []
  for (const [a, curDecComplex] of EVAL_DEC_COMPLEX.entries()) {
    for (const [b, curNetwork] of EVAL_NETWORK_TYPE.entries()) {
      let networkData = curNetwork.data
      for (const [c, curLoss] of EVAL_LOSS_PERCENTAGE.entries()) {
        for (const [d, plcLabel] of EVAL_NORMAL_AND_PLC.entries()) {
          const usePlc = plcLabel === 'plc'
          try {
            const json = JSON.parse(networkData)
            json.down.loss.percentage = curLoss
            networkData = JSON.stringify(json)
          } catch { /* invalid JSON — skip mutation */ }
          const test = createTestPlc(a * b * c + d, curDecComplex, usePlc, curNetwork.name, networkData)
          if (configs.value.length < MAX_CONFIG_SIZE) configs.value.push(test)
          else configsBuffer.value.push(test)
        }
      }
    }
  }
}

function generateSampleConfigsForDred() {
  configs.value = []
  configsBuffer.value = []
  for (const [a, curComplex] of EVAL_COMPLEX.entries()) {
    for (const [b, curDecComplex] of EVAL_DEC_COMPLEX.entries()) {
      for (const [c, curDredDur] of EVAL_DRED.entries()) {
        for (const [d, curNetwork] of EVAL_NETWORK_TYPE.entries()) {
          let networkData = curNetwork.data
          for (const [f, rtt] of EVAL_RTT.entries()) {
            try {
              const json = JSON.parse(networkData)
              json.down.delay.delay = rtt
              for (const [e, loss] of EVAL_LOSS_PERCENTAGE.entries()) {
                json.down.loss.percentage = loss
                networkData = JSON.stringify(json)
                const test = createTestDred(a * b * c * d + e, curComplex, curDecComplex, curDredDur, curNetwork.name, networkData)
                if (configs.value.length < MAX_CONFIG_SIZE) configs.value.push(test)
                else configsBuffer.value.push(test)
              }
            } catch { /* skip on parse error */ }
          }
        }
      }
    }
  }
}

// For every ATC network config: 10 paired loss/delay sub-cases, run with
// Opus PLC enabled for all of them, then the same set again with PLC off.
function generateFullSweepConfigs() {
  configs.value = []
  configsBuffer.value = []
  let index = 0
  for (const usePlc of [true, false]) {
    for (const curNetwork of EVAL_NETWORK_TYPE) {
      for (let i = 0; i < EVAL_SUBCASE_LOSS.length; i++) {
        let networkData = curNetwork.data
        try {
          const json = JSON.parse(networkData)
          json.down.loss.percentage = EVAL_SUBCASE_LOSS[i]
          json.down.delay.delay = String(EVAL_SUBCASE_DELAY[i])
          networkData = JSON.stringify(json)
        } catch { /* invalid JSON — skip mutation */ }
        const test = createTestPlc(index, 6, usePlc, curNetwork.name, networkData)
        if (configs.value.length < MAX_CONFIG_SIZE) configs.value.push(test)
        else configsBuffer.value.push(test)
        index++
      }
    }
  }
}

// ── CRUD ──────────────────────────────────────────────────────────────────────

function addTest() {
  configs.value.push(createTest(configs.value.length))
  numTests.value = String(parseInt(numTests.value, 10) + 1)
  expanded.value.push(configs.value.length - 1)
}

function resetTests() {
  for (const test of configs.value) {
    test.taskId    = ''
    test.result    = null
    test.cancelled = false
    test.status    = TEST_STATUS.PENDING
  }
}

async function deleteTest(index) {
  try { await deleteShape({ ip: props.deviceIp }) } catch { /* best-effort */ }
  stopAndroidApp(index)
  configs.value.splice(index, 1)
  expanded.value = configs.value.map((_, i) => i)
  numTests.value = String(parseInt(numTests.value, 10) - 1)
}

// ── app control ───────────────────────────────────────────────────────────────

async function stopAndroidApp(index) {
  try { await deleteShape({ ip: props.deviceIp }) } catch { /* best-effort */ }
  try {
    if (configs.value[index].taskId)
      await stopApp(configs.value[index].taskId)
  } catch { /* best-effort */ }
  configs.value[index].taskId    = ''
  configs.value[index].result    = null
  configs.value[index].cancelled = true
  configs.value[index].status    = TEST_STATUS.PENDING
}

async function startAndroidApp(index) {
  const test = configs.value[index]
  if (test.status === TEST_STATUS.TESTING) return

  test.cancelled = false
  test.result    = null

  let totalDelay = 0
  let atcConfigName = ''

  const timers = test.atcConfigs.map(({ select, timer, jsonData }) => {
    if (select?.length) {
      const selectString = select.split('.')[0]
      atcConfigName = atcConfigName ? `${atcConfigName}-${selectString}` : selectString
    }
    try {
      const data = JSON.parse(jsonData)
      atcConfigName += `_loss-${data.down.loss.percentage}_rtt-${data.down.delay.delay}`
    } catch {
      atcConfigName += '_loss-0_rtt-0'
    }
    const delay = Math.max((timer.h * 3600 + timer.m * 60 + timer.s) * 1000, DEFAULT_ATC_TIMEOUT)
    totalDelay += delay
    return delay
  })

  const shouldPullAudio = pullAudio.value

  try {
    test.status = TEST_STATUS.TESTING
    test.result = null

    const startAppRes = await runApp(props.deviceId, {
      time:          totalDelay / 1000,
      enableOpusPlc: test.enableOpusPlc,
      folderName:    atcConfigName,
      complexity:    test.complexity,
      decComplexity: test.decComplexity,
      dredDuration:  test.dredDuration,
      pullAudio:     shouldPullAudio,
    })

    const isAccepted = startAppRes?.status === 'started' || startAppRes?.status === 'queued'
    if (!isAccepted) throw new Error('Android App: Cannot start App')

    test.taskId = startAppRes.taskId
    console.log(test)

    for (let j = 0; j < test.atcConfigs.length; j++) {
      if (test.cancelled) return
      const curConfig = test.atcConfigs[j]
      if (curConfig.jsonData) {
        await applyConfig({ data: JSON.parse(curConfig.jsonData), ip: props.deviceIp })
      }
      await new Promise(resolve => setTimeout(resolve, timers[j]))
      if (test.cancelled) return
    }

    if (test.cancelled) return
    try { await deleteShape({ ip: props.deviceIp }) } catch { /* best-effort */ }

    await new Promise(resolve => setTimeout(resolve, 5000))

    let runAppRes = null
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      if (test.cancelled) return
      runAppRes = await getAppRes(startAppRes.taskId)

      if (runAppRes?.status === 'done' && !shouldPullAudio) {
        test.result = {
          status:     RES_STATUS.SUCCESS,
          audioFiles: [],
          logFile:    runAppRes.result?.zrtcLog?.[0] ?? null,
        }
        test.status = TEST_STATUS.PASS
        break
      } else if (runAppRes?.status === 'done' && runAppRes.result.audioFiles?.length > 0 && runAppRes.result.zrtcLog?.length > 0) {
        test.result = {
          status:     RES_STATUS.SUCCESS,
          audioFiles: runAppRes.result.audioFiles,
          logFile:    runAppRes.result.zrtcLog[0],
        }
        test.status = TEST_STATUS.PASS
        break
      } else if (runAppRes?.status === 'done' && !runAppRes.result.zrtcLog?.length) {
        const err = new Error('Error pulling audio files')
        err.storeFolder = runAppRes.result.zrtcLog?.[0]?.split('/').slice(-2, -1).join('/')
        throw err
      }

      if (attempt < MAX_RETRIES) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
      } else {
        throw new Error('Max retries reached')
      }
    }
  } catch (err) {
    if (err.storeFolder) removeFolder(err.storeFolder)
    if (test.cancelled) return
    test.result = { status: RES_STATUS.FAILED, errorMessage: err.message }
    test.status = TEST_STATUS.FAIL
  }

  try {
    if (test.taskId) await stopApp(test.taskId)
    test.taskId = ''
  } catch { /* best-effort */ }
}

async function runTests() {
  resetTests()
  const totalTests = configs.value.length + configsBuffer.value.length
  let factor = 0

  for (let i = 0; i < totalTests; i++) {
    if (i === MAX_CONFIG_SIZE * (factor + 1)) {
      configs.value = configsBuffer.value.splice(0, MAX_CONFIG_SIZE)
      try { await moveAudios(props.deviceId) } catch { /* best-effort */ }
      factor++
    }
    const idx = i - MAX_CONFIG_SIZE * factor

    while (!configs.value[idx].cancelled) {
      await startAndroidApp(idx)
      await new Promise(resolve => setTimeout(resolve, DEFAULT_REQUEST_TIMEOUT))
      if (configs.value[idx].status === TEST_STATUS.PASS) break
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY))
    }
  }
}

function openToast(componentName = '', header = '', message = '', timeout = TOAST_TIMEOUT) {
  emit(EVENT_OPEN_TOAST, 'ConfigAndRun', header, message, timeout)
}

onMounted(generateConfigs)
</script>
