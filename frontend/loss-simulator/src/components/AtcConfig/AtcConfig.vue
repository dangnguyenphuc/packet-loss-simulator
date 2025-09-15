<template>
  <v-container class="d-flex flex-column ga-3">
    <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0 ga-3">
      <v-col cols="1" class="d-flex justify-center align-center">
        <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact" :disabled="!!result"></v-btn>
      </v-col>
      <v-col class="d-flex flex-column justify-start align-start ga-2">
        <v-row class="d-flex">
          <v-select 
          v-model="row.select" 
          :items="selectorOptions" 
          item-title="title"
          item-value="value"
          label="Atc Config" 
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
      <v-col cols="6" md="7" xs="12">
        <Editor v-model="row.jsonData"/>
      </v-col>
      
    </v-row>
    <v-row  v-if="!result" class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" icon="mdi-plus" @click="addRow"></v-btn>
      <v-btn density="compact" icon="mdi-restart" @click="resetRows" :disabled="disableApply"></v-btn>
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
import { EVENT_OPEN_TOAST } from "../../constants/constant"

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
        timer: { h: 0, m: 0, s: 5 },
      });
    },
    deleteRow(index) {
      this.rows.splice(index, 1);
    },
    resetRows() {
      this.rows = [];
    },

    async onConfigSelected(row, value) {
      try {
        const res = await fetchJsonContent(value);
        if (!res || !res.data) {
          throw new Error (`Missing field when get json file: ${value}`);
        }

        row.jsonData = JSON.stringify(res.data, null, 2);

      } catch (err) {
        this.$emit(EVENT_OPEN_TOAST, "Error Getting Json file content", err.message);
      }
    }
  },
  computed: {
    disableApply() {
      return this.rows.length === 0;
    },
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