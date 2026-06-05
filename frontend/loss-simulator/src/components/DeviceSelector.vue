<template>
  <v-row class="pa-3" align="center" justify="center">
    <v-col class="d-flex align-center ga-3">
      <v-row class="d-flex ga-3">
        <v-col class="d-flex">
          <v-select
            label="Choose device"
            v-model="selectedDevice"
            :items="devices"
            :disabled="loadingDevices"
            hide-details
          />
        </v-col>
        <v-col class="d-flex">
          <v-select
            label="Choose IP"
            v-model="selectedIp"
            :items="ips"
            :disabled="loadingIps"
            item-title="text"
            item-value="ip"
            hide-details
          />
        </v-col>
        <v-col cols="1" class="d-flex justify-center align-center">
          <v-btn color="primary" icon="mdi-restart" @click="fetchDevicesData" :disabled="loadingDevices" />
        </v-col>
      </v-row>
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, watch } from 'vue'
import { fetchDevices, fetchDeviceIp } from '../utils/specific.js'
import {
  EVENT_OPEN_TOAST, EVENT_FETCH_DEVICE,
  EVENT_UPDATE_DEVICE, EVENT_UPDATE_DEVICE_IP,
} from '../constants/constant.js'

const emit = defineEmits([EVENT_OPEN_TOAST, EVENT_FETCH_DEVICE, EVENT_UPDATE_DEVICE, EVENT_UPDATE_DEVICE_IP])

const devices       = ref([])
const ips           = ref([])
const loadingDevices = ref(false)
const loadingIps    = ref(false)
const selectedDevice = ref('')
const selectedIp    = ref('')

watch(selectedDevice, fetchDeviceIps)
watch(selectedIp, ip => emit(EVENT_UPDATE_DEVICE_IP, ip))

async function fetchDevicesData() {
  emit(EVENT_FETCH_DEVICE, false)
  selectedDevice.value = ''
  loadingDevices.value = true
  try {
    const { data } = await fetchDevices()
    devices.value = data
    if (data.length > 0) {
      selectedDevice.value = data[0]
      emit(EVENT_UPDATE_DEVICE, selectedDevice.value)
    } else {
      selectedIp.value = ''
      ips.value = []
      throw new Error('No devices found')
    }
  } catch (err) {
    emit(EVENT_OPEN_TOAST, 'DeviceSelector', 'Get devices failed', `Error: ${err.message}`)
  } finally {
    loadingDevices.value = false
  }
}

async function fetchDeviceIps(device) {
  emit(EVENT_FETCH_DEVICE, false)
  selectedIp.value = ''
  if (!device) {
    ips.value = []
    return
  }
  loadingIps.value = true
  try {
    const { data } = await fetchDeviceIp(device)
    ips.value = data
      .filter(ip => ip.ip.startsWith('10.42'))
      .map(ip => ({ ip: ip.ip, text: `${ip.interface}-${ip.ip}` }))
    if (ips.value.length > 0) {
      selectedIp.value = ips.value[0].ip
      emit(EVENT_FETCH_DEVICE, true)
    } else {
      throw new Error('No matching IP addresses found')
    }
  } catch (err) {
    emit(EVENT_OPEN_TOAST, 'DeviceSelector', 'Get device IP failed', `Error: ${err.message}`)
  } finally {
    loadingIps.value = false
  }
}

fetchDevicesData()
</script>
