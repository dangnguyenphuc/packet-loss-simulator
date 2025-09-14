<template>
  <v-container class="d-flex flex-column ga-3">
    <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0 ga-3">
      <v-col class="d-flex justify-center align-center pa-0">
        <v-select v-model="row.select" :items="definedConfig" label="Atc Config" hide-details></v-select>
      </v-col>
      <v-col >
        <Editor v-model="row.jsonData"/>
      </v-col>
      <v-col class="d-flex justify-center align-center pa-0">
        <Timer :hour="row.timer.h" :minute="row.timer.m" :second="row.timer.s"/>
      </v-col>
      <v-col cols="1" class="d-flex justify-center align-center">
        <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact" :disabled="!!result"></v-btn>
      </v-col>
    </v-row>
    <v-row  v-if="!result" class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" icon="mdi-plus" @click="addRow"></v-btn>
      <v-btn density="compact" icon="mdi-undo" @click="resetRows" :disabled="disableApply"></v-btn>
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

export default {
  name: "AtcConfig",
  components: {Editor, Timer, Result},
  props: {
    modelValue: {
      required: true,
    },
    definedConfig: {
      default: ["1", "2", "3"]
    },
    result: {
      required: true
    }
  },
  data() {
    return {
        rows: this.modelValue,
        selectorOptions: ["1", "2", "3"],
        RES_STATUS,
    };
  },
  methods: {
    addRow() {
      this.rows.push({
        id: Date.now(),
        select: null,
        jsonData: "",
        timer: { h: 0, m: 0, s: 30 },
      });
    },
    deleteRow(index) {
      this.rows.splice(index, 1);
    },
    resetRows() {
      this.rows = [];
    },
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
      }
  },
};
</script>

