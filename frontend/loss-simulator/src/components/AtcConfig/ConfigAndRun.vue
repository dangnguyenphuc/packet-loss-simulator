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
          :key="test.id"
          :value="index"
        >
          <!-- Title -->
          <v-expansion-panel-title>
            <v-row class="w-100 d-flex align-center">
              <v-col cols="6"> Test #{{ index + 1 }} </v-col>
              <v-col cols="6" class="d-flex justify-end align-center ga-2">
                <v-btn 
                  @click.stop="deleteTest(index)" 
                  color="red" 
                  icon="mdi-delete" 
                  density="compact"
                />
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
            <AtcConfig 
              @open:Toast="openToast" 
              v-model="test.atcConfigs" 
              :result="test.result" 
              :definedConfig="atcConfigs"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-row>

    <!-- Controls -->
    <v-row class="pa-0">
      <v-col class="d-flex flex-row justify-start align-center ga-3">
        <v-btn color="green" variant="tonal" @click="addTest">Add Test</v-btn>
      </v-col>
      <v-col class="d-flex flex-row justify-end align-center ga-3">
        <v-btn color="primary" @click="runTests" :disabled="this.configs.length === 0">Run</v-btn> 
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { TEST_STATUS, RES_STATUS } from "../../constants/enums";
import { DEFAULT_ATC_TIMEOUT, EVENT_OPEN_TOAST, TOAST_TIMEOUT, MAX_RETRIES, RETRY_DELAY } from "../../constants/constant"
import AtcConfig from "./AtcConfig.vue";
import Result from "./Result.vue";
import { applyConfig, deleteShape, runApp, getAppRes } from "../../utils/specific";

export default {
  name: "ConfigAndRun",
  props: {
    atcConfigs: { default: [] },
    deviceId: { required: true, type: String },
    deviceIp: { required: true, type: String }
  },
  components: { AtcConfig, Result },
  data() {
    return {
      numTests: "0",
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
      this.configs = Array.from({ length: count }, (_, i) => this.createTest(i));
      this.expanded = this.configs.map((_, i) => i);
    },

    createTest(i = 0) {
      return {
        id: Date.now() + i,
        status: TEST_STATUS.PENDING,
        atcConfigs: [
          {
            id: Date.now() + "_" + i,
            select: null,
            jsonData: "",
            timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT/1000 },
          }
        ],
        result: null,
      };
    },

    addTest() {
      if (this.configs.length >= 10) {
        this.openToast("Limit Reached", "You can only add up to 10 tests");
        return;
      }
      const newTest = this.createTest(this.configs.length);
      this.configs.push(newTest);
      this.numTests = (parseInt(this.numTests, 10) + 1).toString();
      this.expanded.push(this.configs.length - 1);
    },

    async runTests() {
      for (let i = 0; i < this.configs.length; i++) {
        const test = this.configs[i];
        let totalDelay = 0;
        const timers = test.atcConfigs.map(({ timer }) => {
          const { h, m, s } = timer;
          let delay = (h * 3600 + m * 60 + s) * 1000;
          if (delay <= 0) {
            delay = DEFAULT_ATC_TIMEOUT;
          }
          totalDelay += delay;
          return delay;
        });
        try {
          this.configs[i].status = TEST_STATUS.TESTING;
          this.configs[i].result = null;
          const startAppRes = await runApp({
            deviceId: this.deviceId,
            time: totalDelay / 1000
          });
          
          if (!startAppRes || startAppRes.status !== "started") {
            throw new Error("Android App: Cannot start App");
          }
          for (let j = 0; j < test.atcConfigs.length; j++) {
            const curConfig = test.atcConfigs[j];

            await applyConfig({
              data: JSON.parse(curConfig.jsonData || "{}"),
              ip: this.deviceIp,
            });
            // wait timer for this config
            await new Promise((resolve) => setTimeout(resolve, timers[j]));
          }
          
          try {
            await deleteShape({ ip: this.deviceIp });
          } catch {}

          let runAppRes = null;

          for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            runAppRes = await getAppRes(startAppRes.taskId);

            if (
              runAppRes &&
              runAppRes.status === "done" &&
              runAppRes.result.audioFiles?.length > 0 &&
              runAppRes.result.zrtcLog?.length > 0
            ) {
              // Success, break the retry loop
              break;
            }

            if (attempt < MAX_RETRIES) {
              // Wait before retrying
              await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
            }
          }

          // After retries, validate result
          if (
            !runAppRes ||
            runAppRes.status !== "done" ||
            !runAppRes.result.audioFiles?.length ||
            !runAppRes.result.zrtcLog?.length
          ) {
            throw new Error("Android App: run fail or missing audio/log files");
          }

          // Success
          test.result = {
            status: RES_STATUS.SUCCESS,
            audioFiles: runAppRes.result.audioFiles,
            logFile: runAppRes.result.zrtcLog[0],
          };
          test.status = TEST_STATUS.PASS;
        } catch (err) {
          test.result = {
            status: RES_STATUS.FAILED,
            errorMessage: err.message,
          };
          test.status = TEST_STATUS.FAIL;
        }
      }
    },
    
    deleteTest(index) {
      this.configs.splice(index, 1);
      this.expanded = this.configs.map((_, i) => i);
      this.numTests = (parseInt(this.numTests, 10) - 1).toString();
    },

    openToast(componentName="", header = "", message = "", timeout = TOAST_TIMEOUT) {
      this.$emit(EVENT_OPEN_TOAST, this.$options.name, header, message, timeout);
    },
  },
  watch: {
    
  },
  async mounted() {
    await this.generateConfigs();
  }
};
</script>
