<template>
  <v-container>
    <v-row class="d-flex flex-column justify-center align-start ga-3">
        <v-checkbox
            v-model="enableAutoStop"
            label="Auto Stop"
        />
        <v-btn density="compact" color="black" prepend-icon="mdi-record-circle" @click="startCaptureAll" :disabled="isStartCaptureAll">Start Capture All</v-btn>
        <v-btn density="compact" color="red" prepend-icon="mdi-pause-circle" @click="stopCaptureAll">Stop Capture All</v-btn>
        <v-btn density="compact" color="green" prepend-icon="mdi-reload" @click="resetAll" >Reset All</v-btn>
    </v-row>
    <v-row>
      <v-col
        v-for="(graph, index) in graphs"
        :key="index"
        cols="6"
        md="12"
      >
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

<script>
import LineGraph from './LineGraph.vue'
import {
  EVENT_START_MONITORING,
  EVENT_STOP_MONITORING,
  EVENT_RESET_MONITORING,
  RETRY_DELAY,
  BENCHMARK_DURATION,
} from '../../constants/constant'
import { getStat } from '../../utils/specific';

export default {
  name: 'Monitor',
  props: {
    deviceId: {
      type: String,
      required: true
    }
  },
  components: { LineGraph },
  data() {
    return {
      EVENT_START_MONITORING,
      EVENT_STOP_MONITORING,
      EVENT_RESET_MONITORING,
      isStartCaptureAll: false,
      enableAutoStop: true,
      autoStopTimer: null,
      // list of graphs - each title must be different
      graphs: [
        {
          title: 'mem',
          series: [
            {
              name: 'Used memory MB',
              data: [],
            },
          ],
          timer: null, // for individual interval tracking
        },
        {
          title: 'cpu',
          series: [
            {
              name: 'Used CPU %',
              data: [],
            },
          ],
          timer: null,
        },
      ],
    }
  },
  methods: {
    async startCaptureAll() {
      try {
        await getStat({
          type: "start",
          id: this.deviceId,
        });
      } catch (e) {}

      if (this.autoStopTimer) {
        clearTimeout(this.autoStopTimer);
      }

      for (let graph of this.graphs)
      {
          await this.startCapture(graph.title);
      }
      this.isStartCaptureAll = true;

      if (this.enableAutoStop) {
        this.autoStopTimer = setTimeout(async () => {
          await this.stopCaptureAll();
        }, BENCHMARK_DURATION);
      }
      
    },

    async stopCaptureAll() {
      for (let graph of this.graphs)
      {
          this.stopCapture(graph.title);   
      }
      this.isStartCaptureAll = false;
      try {
        await getStat({
          type: "stop",
          id: this.deviceId,
        });
      } catch (e) {}
    },
    
    resetAll() {
      for (let graph of this.graphs)
      {
          this.resetMonitor(graph.title);   
      }
      this.isStartCaptureAll = false;
    },

    async startCapture(type) {
      const graph = this.graphs.find((g) => g.title === type)
      if (!graph) return

      if (graph.timer) {
        console.log(`Timer for ${type} already running.`)
        return
      }

      console.log(`▶️ Start capture for ${type}`)

      graph.timer = setInterval(async () => {
        try {
            const res = await getStat({
              type: type,
              id: this.deviceId,
            });

            if (
                !res || 
                !res.hasOwnProperty("data") || 
                !res.data ||
                res.data < 0
            ) throw new Error("");

            const series = graph.series[0].data

            series.push(res.data)

            graph.series = [{ ...graph.series[0], data: [...series] }]

        } catch (e) {}
        
      }, RETRY_DELAY)
    },

    stopCapture(type) {
      const graph = this.graphs.find((g) => g.title === type)
      if (!graph || !graph.timer) return

      clearInterval(graph.timer)
      graph.timer = null
      console.log(`⏸️ Stop capture for ${type}`)
    },

    resetMonitor(type) {
      const graph = this.graphs.find((g) => g.title === type)
      clearInterval(graph.timer)
      graph.timer = null
      console.log(`⏸️ Stop capture for ${type}`)
      graph.series = [{...graph.series[0], data: []}];
    },
  },
  beforeDestroy() {
    // Clean up all timers when component unmounts
    this.graphs.forEach((g) => {
      if (g.timer) clearInterval(g.timer)
    })
  },
}
</script>
