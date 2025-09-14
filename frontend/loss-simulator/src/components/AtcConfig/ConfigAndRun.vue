<template>
  <v-container class="d-flex flex-column ga-3">
    <!-- Input -->
    <v-row>
      <v-col cols="12" md="4">
        <v-text-field
          v-model="numTests"
          type="text"
          label="Number of Tests (0 - 10)"
          @input="validateNumTests"
        />
      </v-col>
    </v-row>

    <!-- Panels -->
    <v-row>
      <v-expansion-panels v-model="expanded" multiple>
        <v-expansion-panel
          v-for="(test, index) in configs"
          :key="index"
          :value="index"
        >
          <!-- Title -->
          <v-expansion-panel-title>
            <v-row class="w-100 d-flex align-center">
              <v-col cols="6"> Test #{{ index + 1 }} </v-col>
              <v-col cols="6" class="d-flex justify-end align-center">
                <v-progress-circular
                  v-if="test.status === TEST_STATUS.TESTING"
                  indeterminate
                  color="primary"
                  size="20"
                  width="2"
                />
                <v-icon v-else-if="test.status === TEST_STATUS.PASS" color="green">
                  mdi-check-circle
                </v-icon>
                <v-icon v-else-if="test.status === TEST_STATUS.FAIL" color="red">
                  mdi-close-circle
                </v-icon>
                <v-icon v-else-if="test.status === TEST_STATUS.PENDING" color="grey">
                  mdi-help-circle
                </v-icon>
              </v-col>
            </v-row>
          </v-expansion-panel-title>

          <!-- Panel Content -->
          <v-expansion-panel-text>
            <AtcConfig v-model="test.atcConfigs" :result="test.result"/>
            
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>

    <!-- Controls -->
    <v-row>
      <v-col>
        <v-btn color="primary" @click="runTests">Run</v-btn>
        <v-btn color="red" variant="tonal" @click="resetTests">
          Reset
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { TEST_STATUS, RES_STATUS } from "../../constants/enums";
import AtcConfig from "./AtcConfig.vue";
import Result from "./Result.vue";

export default {
  name: "ConfigAndRun",
  components: { AtcConfig, Result },
  data() {
    return {
      numTests: "1",
      configs: [],
      expanded: [],
      TEST_STATUS,
      RES_STATUS,
    };
  },
  methods: {
    validateNumTests() {
      let value = parseInt(this.numTests, 10);
      if (isNaN(value)) value = 0;
      if (value < 0) value = 0;
      if (value > 10) value = 10;

      this.numTests = value.toString();
      this.generateConfigs();
    },

    generateConfigs() {
      const count = parseInt(this.numTests, 10) || 0;
      this.configs = Array.from({ length: count }, () => ({
        status: TEST_STATUS.PENDING,
        atcConfigs: [
          {
            id: Date.now(),
            select: null,
            jsonData: "{}",
            timer: { h: 0, m: 0, s: 30 },
          }
        ],
        result: null,
      }));
      this.expanded = this.configs.map((_, i) => i);
    },

    async runTests() {
      for (let i = 0; i < this.configs.length; i++) {
        this.configs[i].status = TEST_STATUS.TESTING;
        this.configs[i].results = null;

        await new Promise((resolve) => setTimeout(resolve, 2000));

        const didPass = Math.random() > 0.4;
        this.configs[i].status = didPass
          ? TEST_STATUS.PASS
          : TEST_STATUS.FAIL;

        this.configs[i].result = didPass
          ?
            {
              status: RES_STATUS.SUCCESS,
              audioFiles: ["audio1.mp3", "audio2.mp3"],
              selectedAudio: "audio1.mp3",
              logFile: `run_${i}_2025_09_14.log`,
            }
          :
            {
              status: RES_STATUS.FAILED,
              errorMessage: `ERR_CODE_${1000 + i}: Simulation failed`,
            };
      }
    },

    resetTests() {
      this.generateConfigs();
    },
  },
  mounted() {
    this.generateConfigs();
  },
};
</script>
