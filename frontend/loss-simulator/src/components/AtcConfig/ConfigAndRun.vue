<template>
  <v-container v-if="display" class="d-flex flex-column ga-3">
    <!-- Input -->
     {{ deviceId }} {{ deviceIp }}
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
          :key="test.id"
          :value="index"
        >
          <!-- Title -->
          <v-expansion-panel-title>
            <v-row class="w-100 d-flex align-center">
              <v-col cols="6"> Test #{{ index + 1 }} </v-col>
              <v-col cols="6" class="d-flex justify-end align-center ga-2">
                <v-btn @click.stop="deleteTest(index)" color="red" icon="mdi-delete" density="compact"></v-btn>
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
            <AtcConfig @open:Toast="openToast" v-model="test.atcConfigs" :result="test.result" :definedConfig="atcConfigs"/>
            
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>

    <!-- Controls -->
    <v-row>
      <v-col class="d-flex flex-row justify-center align-center ga-3">
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
import { DEFAULT_ATC_TIMEOUT, EVENT_OPEN_TOAST, TOAST_TIMEOUT } from "../../constants/constant"
import AtcConfig from "./AtcConfig.vue";
import Result from "./Result.vue";
import { applyConfig, deleteShape } from "../../utils/specific";

export default {
  name: "ConfigAndRun",
  props: {
    display: {
      required: true,
    },
    atcConfigs: {
      default: []
    },
    deviceId: {
      required: true,
      type: String,
    },
    deviceIp: {
      required: true,
      type: String
    }
  },
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
      this.configs = Array.from({ length: count }, (_, i) => ({
        id: Date.now() + i,
        status: TEST_STATUS.PENDING,
        atcConfigs: [
          {
            id: Date.now() + "_" + i,
            select: null,
            jsonData: "",
            timer: { h: 0, m: 0, s: 5 },
          }
        ],
        result: null,
      }));
      this.expanded = this.configs.map((_, i) => i);
    },

    
    async runTests() {
      for (let i = 0; i < this.configs.length; i++) {
        // each test
        const test = this.configs[i];
        try {
          this.configs[i].status = TEST_STATUS.TESTING;
          this.configs[i].result = null;
  
          for (let j = 0; j < test.atcConfigs.length; j+= 1) {
            console.log(`config${j}`);
            const curConfig = test.atcConfigs[j];
            const { h, m, s } = curConfig.timer;
            const delay = (h * 3600 + m * 60 + s) * 1000;
            if (delay <= 0) {
              delay = DEFAULT_ATC_TIMEOUT;
              this.openToast(`Test ${i}`, `Invalid delay, set time to default: ${DEFAULT_ATC_TIMEOUT}`);
            }
            await applyConfig({
              data: JSON.parse(curConfig.jsonData),
              ip: this.deviceIp
            });
            await new Promise((resolve) => setTimeout(resolve, delay));
            continue;
          }

          deleteShape({
            ip: this.deviceIp
          })

          test.result = {
            status: RES_STATUS.SUCCESS,
            audioFiles: ["audio1.mp3", "audio2.mp3"],
            selectedAudio: "audio1.mp3",
            logFile: `run_${i}_2025_09_14.log`,
          };
          test.status = TEST_STATUS.PASS;

        } catch (err) {
          test.result = {
              status: RES_STATUS.FAILED,
              errorMessage: err.message,
          }
          test.status = TEST_STATUS.FAIL;
        }
      }
    },

    resetTests() {
      this.generateConfigs();
    },

    deleteTest(index) {
      this.configs.splice(index, 1);
      this.expanded = this.configs.map((_, i) => i);
      this.numTests = (parseInt(this.numTests, 10) - 1).toString();
    },

    openToast(header = "", message = "", timeout = TOAST_TIMEOUT) {
      this.$emit(EVENT_OPEN_TOAST, header, message, timeout);
    },
  },
  watch: {
    display(newVal) {
      if (newVal) this.generateConfigs();
    },
  }
};
</script>
