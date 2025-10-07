<template>
  <v-card class="pa-3">
    <v-card-title>{{ graphTitle }}</v-card-title>
    <v-card-text>
      <div id="chart">
        <apexchart
          type="line"
          height="350"
          :options="chartOptions"
          :series="series"
        ></apexchart>
      
        <v-row class="d-flex justify-space-between align-center gap-3">
          <v-btn density="compact" color="black" prepend-icon="mdi-record-circle" @click="startCapture" :disabled="isStartCapture">Start capture</v-btn>
          <v-btn  density="compact" color="red" prepend-icon="mdi-pause-circle" @click="stopCapture" :disabled="!isStartCapture">Stop capture</v-btn>
          <v-btn  density="compact" color="green" prepend-icon="mdi-reload" @click="reset" :disabled="isStartCapture">Reset</v-btn>
        </v-row>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
import VueApexCharts from 'vue3-apexcharts'
import { EVENT_START_MONITORING, EVENT_STOP_MONITORING, EVENT_RESET_MONITORING } from '../../constants/constant';


export default {
  name: 'LineGraph',
  components: {
    apexchart: VueApexCharts,
  },
  props: {
    graphTitle: {
      type: String,
      default: '',
    },
    series: {
      type: Array,
      default: () => [
        {
          name: 'Series 1',
          data: [],
        },
      ],
    },
  },
  data() {
    return {
      chartOptions: {
        chart: {
          height: 350,
          type: 'line',
          zoom: {
            enabled: false,
          },
        },
        dataLabels: {
          enabled: false,
        },
        stroke: {
          curve: 'straight',
        },
        grid: {
          row: {
            colors: ['#f3f3f3', 'transparent'],
            opacity: 0.5,
          },
        },
      },
      isStartCapture: false,
    }
  },
  methods: {
    startCapture() {
      this.$emit(EVENT_START_MONITORING, this.graphTitle);
      this.isStartCapture = true;
    },

    stopCapture() {
      this.$emit(EVENT_STOP_MONITORING, this.graphTitle);
      this.isStartCapture = false;
    },
    
    reset() {
      this.$emit(EVENT_RESET_MONITORING, this.graphTitle);
      this.isStartCapture = false;
    },
  }
}
</script>
