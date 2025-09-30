<template>
  <v-container class="d-flex flex-column ga-3">
    <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0 ga-3">
      <v-col cols="1" class="d-flex justify-center align-center">
        <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact" :disabled="!!result"></v-btn>
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
        <Editor v-model="row.jsonData"/>
      </v-col>
      
    </v-row>
    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" icon="mdi-plus" @click="addRow"></v-btn>
      <v-btn density="compact" icon="mdi-restart" @click="resetRows"></v-btn>
    </v-row>
    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" color="red" prepend-icon="mdi-stop-circle" @click='stopApp' :disabled="taskId.length <= 0">Stop</v-btn>
      <v-btn density="compact" color="green" prepend-icon="mdi-play-circle" @click='startApp' :disabled="taskId != '' && !result">Run Test</v-btn>
    </v-row>
    <v-row>
      <Result v-if="result" :result="result" />
    </v-row>
  </v-container>
</template>

<script>
import Editor from '../Editor.vue';
import Timer from '../Timer.vue';
import Result from './Result.vue'
import { RES_STATUS } from "../../constants/enums";
import { fetchJsonContent } from '../../utils/specific';
import { EVENT_OPEN_TOAST, EVENT_UPDATE_MODEL, DEFAULT_ATC_TIMEOUT, EVENT_STOP_APP, EVENT_START_APP } from "../../constants/constant"

export default {
  name: "AtcConfig",
  components: {Editor, Timer, Result},
  props: {
    modelValue: {
      required: true,
    },
    definedConfig: {
      default: []
    },
    result: {
      required: true
    },
    taskId: {
      required: true
    }
  },
  data() {
    return {
        rows: this.modelValue,
        curOptions: this.definedConfig,
        selectorOptions: this.definedConfig.map(path => (path.split('/').pop())),
        RES_STATUS,
    };
  },
  methods: {
    addRow() {
      this.rows.push({
        id: Date.now(),
        select: null,
        jsonData: "",
        timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT/1000 },
      });
    },
    deleteRow(index) {
      this.rows.splice(index, 1);
    },
    resetRows() { 
      this.rows = [];
      this.addRow();
    },

    async onConfigSelected(row, value) {
      try {
        const res = await fetchJsonContent(value);
        if (!res || !res.data) {
          throw new Error (`Missing field when get json file: ${value}`);
        }

        row.jsonData = JSON.stringify(res.data, null, 2);

      } catch (err) {
        this.$emit(EVENT_OPEN_TOAST, this.$options.name, "Error Getting Json file content", err.message);
      }
    },

    stopApp() {
      this.$emit(EVENT_STOP_APP);
    },

    startApp() {
      this.$emit(EVENT_START_APP);
    }
  },
  watch: {
      rows(newValue) {
          this.$emit(EVENT_UPDATE_MODEL, newValue);
      },
      modelValue(newValue) {
          if (newValue !== this.rows) {
              this.rows = newValue;
          }
      },
      definedConfig(newVal) {
        if (newVal != this.curOptions) {
          this.curOptions = newVal;
          this.selectorOptions = newVal.map(path => (path.split('/').pop()));
        }
      }
  },
  computed: {
  },
};
</script>