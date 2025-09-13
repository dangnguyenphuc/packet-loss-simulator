<template>
  <v-container>
    <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0 ga-3">
      <v-col class="d-flex justify-center align-center pa-0">
        <v-select v-model="row.select" :items="selectorOptions" label="Atc Config" hide-details></v-select>
      </v-col>
      <v-col >
        <Editor v-model="row.jsonData"/>
      </v-col>
      <v-col class="d-flex justify-center align-center pa-0">
        <v-row class="d-flex justify-center align-center pa-0 ga-1">
          <v-col class="d-flex justify-center align-center pa-0">
            <v-text-field v-model.number="row.timer.h" label="H" type="number" min="0" hide-details></v-text-field>
          </v-col>
          <v-col class="d-flex justify-center align-center pa-0">
            <v-text-field v-model.number="row.timer.m" label="M" type="number" min="0" max="59" hide-details></v-text-field>
          </v-col>
          <v-col class="d-flex justify-center align-center pa-0">
            <v-text-field v-model.number="row.timer.s" label="S" type="number" min="0" max="59" hide-details></v-text-field>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="1" class="d-flex justify-center align-center">
        <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact"></v-btn>
      </v-col>
    </v-row>
    <v-row class="d-flex justify-center align-center pa-0 ga-3">
      <v-btn density="compact" icon="mdi-plus" @click="addRow"></v-btn>
      <v-btn density="compact" icon="mdi-undo" @click="resetRows" :disabled="disableApply"></v-btn>
      <v-btn density="compact" prepend-icon="mdi-check" @click="applyRows" :disabled="disableApply">Apply</v-btn>
    </v-row>
  </v-container>
</template>

<script>
import Editor from '../Editor.vue';

export default {
  name: "AtcConfig",
  components: {Editor},
  data() {
    return {
        code: JSON.stringify({"name":"Vuetify + CodeMirror","version":1,"features":["json","format","vuetify"]}, null, 2),
        rows: [
        {
            id: Date.now(),
            select: null,
            jsonData: "{\"heellnaw\": \"dang\"}",
            timer: { h: 0, m: 0, s: 0 },
        },
        ],
        selectorOptions: [],
    };
  },
  methods: {
    addRow() {
      this.rows.push({
        id: Date.now(),
        select: null,
        jsonData: "",
        timer: { h: 0, m: 0, s: 0 },
      });
    },
    deleteRow(index) {
      this.rows.splice(index, 1);
    },
    resetRows() {
      this.rows = [];
    },
    applyRows() {
      console.log("Applying rows:", this.rows);
    },
    formatJson() {
      // No formatting needed, just a placeholder
    },
  },
  computed: {
    disableApply() {
      return this.rows.length === 0;
    },
  },
  watch: {
    code(newVa) {
        console.log(newVa);
    }
  }
};
</script>

