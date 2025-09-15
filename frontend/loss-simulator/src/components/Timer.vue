<template>
  <v-row>
    <v-col cols="12" class="d-flex align-center justify-center ga-3">
      <v-text-field
        type="number"
        v-model="localHour"
        :min="0"
        class="timer-input-field"
        hide-details
      ></v-text-field>
      <span>:</span>
      <v-text-field
        type="number"
        v-model="localMinute"
        :min="0"
        :max="59"
        hide-details
        class="timer-input-field"
      ></v-text-field>
      <span>:</span>
      <v-text-field
        type="number"
        v-model="localSecond"
        :min="0"
        :max="59"
        hide-details
        class="timer-input-field"
      ></v-text-field>
    </v-col>
  </v-row>
</template>

<script>
import { 
    EVENT_UPDATE_TIMER_H,
    EVENT_UPDATE_TIMER_M,
    EVENT_UPDATE_TIMER_S
 } from '../constants/constant';
export default {
  name: "Timer",
  props: {
    hour: {
      type: Number,
      default: 0,
    },
    minute: {
      type: Number,
      default: 0,
    },
    second: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      localHour: this.hour,
      localMinute: this.minute,
      localSecond: this.second,
    };
  },
  watch: {
    localHour(newVal) {
      this.$emit(EVENT_UPDATE_TIMER_H, parseInt(newVal) || 0);
    },
    localMinute(newVal) {
      this.$emit(EVENT_UPDATE_TIMER_M, parseInt(newVal) || 0);
    },
    localSecond(newVal) {
      this.$emit(EVENT_UPDATE_TIMER_S, parseInt(newVal) || 0);
    },
    // keep props reactive if parent updates them
    hour(newVal) {
      this.localHour = newVal;
    },
    minute(newVal) {
      this.localMinute = newVal;
    },
    second(newVal) {
      this.localSecond = newVal;
    },
  },
};
</script>

<style scoped>
.timer-input-field {
  width: 80px;
}
</style>
