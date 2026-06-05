<template>
  <v-row>
    <v-col cols="12" class="d-flex align-center justify-center ga-3">
      <v-text-field type="number" v-model="localHour" :min="0" class="timer-input-field" hide-details />
      <span>:</span>
      <v-text-field type="number" v-model="localMinute" :min="0" :max="59" hide-details class="timer-input-field" />
      <span>:</span>
      <v-text-field type="number" v-model="localSecond" :min="0" :max="59" hide-details class="timer-input-field" />
    </v-col>
  </v-row>
</template>

<script setup>
import { ref, watch } from 'vue'
import { EVENT_UPDATE_TIMER_H, EVENT_UPDATE_TIMER_M, EVENT_UPDATE_TIMER_S } from '../constants/constant'

const props = defineProps({
  hour:   { type: Number, default: 0 },
  minute: { type: Number, default: 0 },
  second: { type: Number, default: 0 },
})

const emit = defineEmits([EVENT_UPDATE_TIMER_H, EVENT_UPDATE_TIMER_M, EVENT_UPDATE_TIMER_S])

const localHour   = ref(props.hour)
const localMinute = ref(props.minute)
const localSecond = ref(props.second)

watch(localHour,   v => emit(EVENT_UPDATE_TIMER_H, parseInt(v) || 0))
watch(localMinute, v => emit(EVENT_UPDATE_TIMER_M, parseInt(v) || 0))
watch(localSecond, v => emit(EVENT_UPDATE_TIMER_S, parseInt(v) || 0))

watch(() => props.hour,   v => { localHour.value   = v })
watch(() => props.minute, v => { localMinute.value = v })
watch(() => props.second, v => { localSecond.value = v })
</script>

<style scoped>
.timer-input-field {
  min-width: 70px;
  max-width: 100px;
}
</style>
