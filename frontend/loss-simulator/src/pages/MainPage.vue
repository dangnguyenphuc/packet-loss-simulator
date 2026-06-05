<template>
  <v-container class="main-container">
    <v-row justify="center">
      <v-col>
        <h1>Hello, {{ username }}!</h1>
      </v-col>
    </v-row>
    <v-expansion-panels v-model="expanded" multiple>
      <v-expansion-panel
        v-for="panel in panels"
        :key="panel.key"
        :value="panel.value"
        :class="panel.class"
      >
        <div v-if="panel.alwaysShow || (selectedDevice && selectedIp)">
          <v-expansion-panel-title>
            <span class="title">{{ panel.title }}</span>
          </v-expansion-panel-title>
          <v-expansion-panel-text eager>
            <component
              :is="panel.component"
              @open:Toast="openToast"
              v-bind="panel.props"
              v-on="panel.events"
            />
          </v-expansion-panel-text>
        </div>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue'
import DeviceSelector from '../components/DeviceSelector.vue'
import Guidance from '../components/Guidance.vue'
import TestInfo from '../components/TestInfo.vue'
import ConfigAndRun from '../components/AtcConfig/ConfigAndRun.vue'
import {
  GUIDE_TEXT, EVENT_OPEN_TOAST, TOAST_TIMEOUT,
  EVENT_UPDATE_DEVICE, EVENT_UPDATE_DEVICE_IP, EVENT_FETCH_DEVICE,
} from '../constants/constant'
import { fetchJsons, fetchUser } from '../utils/specific'

const emit = defineEmits([EVENT_OPEN_TOAST])

const username       = ref('')
const selectedDevice = ref('')
const selectedIp     = ref('')
const expanded       = ref([0, 1])

const panels = reactive([
  {
    key: 0, value: 0, alwaysShow: true,
    title: 'How to use', class: 'intro',
    component: Guidance,
    props: { content: GUIDE_TEXT, deviceId: '' },
    events: {},
  },
  {
    key: 1, value: 1, alwaysShow: true,
    title: 'Device Selector', class: 'device-selector',
    component: DeviceSelector,
    props: {},
    events: {
      [EVENT_UPDATE_DEVICE]:    handleDeviceUpdate,
      [EVENT_UPDATE_DEVICE_IP]: handleDeviceIpUpdate,
      [EVENT_FETCH_DEVICE]:     handleDeviceFetched,
    },
  },
  {
    key: 2, value: 2, alwaysShow: false,
    title: 'Auto test information', class: 'test-info',
    component: TestInfo,
    props: { deviceId: '' },
    events: {},
  },
  {
    key: 3, value: 3, alwaysShow: false,
    title: 'Config ATC and Run Tests', class: 'config-container',
    component: ConfigAndRun,
    props: { atcConfigs: [], deviceId: '', deviceIp: '' },
    events: {},
  },
])

async function loadUsername() {
  try {
    const result = await fetchUser()
    username.value = result.username
  } catch {
    username.value = 'nobody'
  }
}

function handleDeviceUpdate(value) {
  selectedDevice.value    = value
  panels[3].props.deviceId = value
}

function handleDeviceIpUpdate(value) {
  selectedIp.value         = value
  panels[3].props.deviceIp = value
}

async function handleDeviceFetched(value) {
  if (!value) return
  expanded.value = [0, 1, 2, 3]
  try {
    const res = await fetchJsons()
    if (!Object.hasOwn(res, 'files')) throw new Error('Response missing "files" field')
    panels[0].props.deviceId  = selectedDevice.value
    panels[2].props.deviceId  = selectedDevice.value
    panels[3].props.atcConfigs = res.files
  } catch (err) {
    openToast('Error Getting ATC Configs', err.message)
  }
}

function openToast(componentName = '', header = '', message = '', timeout = TOAST_TIMEOUT) {
  if (componentName === 'DeviceSelector') {
    expanded.value = [1]
    panels[2].props.deviceId = ''
    selectedDevice.value = ''
  }
  emit(EVENT_OPEN_TOAST, header, message, timeout)
}

loadUsername()
</script>

<style scoped>
.main-container {
  width: 1200px;
}

@media (max-width: 767px) {
  .main-container {
    width: 600px;
  }
}

@media (max-width: 566px) {
  .main-container {
    width: 350px;
  }
}
</style>
