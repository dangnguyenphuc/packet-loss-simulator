<template>
  <v-container class="d-flex flex-column ga-3">
    <!-- Input -->
    <v-row>
      <v-col class="d-flex justify-center align-center">
        <v-text-field
          v-model="numTests"
          type="text"
          label="Number of Tests"
          hide-details
        />

      </v-col>
      <v-col class="d-flex justify-center align-center">
        <v-btn prepend-icon="$vuetify" @click="validateNumTests">
          Generate Test
        </v-btn>
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
              <v-col> Test #{{ index + 1 }} </v-col>
              <v-col class="d-flex justify-end align-center ga-2">
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
            
            <div class="d-flex justify-center align-center">
              <v-col>
                <v-checkbox
                    v-model="test.enableOpusPlc"
                    label="Enable Opus PLC"
                    class="d-flex align-center justify-start"
                />
              </v-col>
              <v-col class="d-flex justify-center align-center ga-3">
                <span>
                  Complexity
                </span>
                <v-select 
                v-model="test.complexity"
                style="max-width: 100px"
                density="compact"
                :items="complexityOptions" 
                hide-details
              />
              </v-col>
            </div>
            <AtcConfig 
              @open:Toast="openToast"
              @stop:AndroidApp="() => stopAndroidApp(index)"
              @start:AndroidApp="() => startAndroidApp(index)"
              v-model="test.atcConfigs"
              :taskId="test.taskId"
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
        <v-btn color="primary" @click="runTests" :disabled="this.configs.length === 0">Run All Tests</v-btn> 
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { TEST_STATUS, RES_STATUS } from "../../constants/enums";
import { 
  DEFAULT_ATC_TIMEOUT, 
  EVENT_OPEN_TOAST, 
  TOAST_TIMEOUT, 
  MAX_RETRIES, 
  RETRY_DELAY,
  NUMBER_OF_SAMPLE_CONFIGS,
  EVAL_COMPLEX,
  EVAL_LOSS_PERCENTAGE,
  EVAL_NORMAL_AND_PLC,
  EVAL_NETWORK_TYPE,
} from "../../constants/constant"
import AtcConfig from "./AtcConfig.vue";
import Result from "./Result.vue";
import { applyConfig, deleteShape, runApp, getAppRes, stopApp, removeFolder } from "../../utils/specific";

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
      complexityOptions: Array.from({ length: 10 }, (_, i) => i + 1),
    };
  },
  methods: {
    validateNumTests() {
      if (this.numTests === "test") {
        this.generateSampleConfigs();
      } else {
        try {
          let value = parseInt(this.numTests, 10);
          if (value < 0) value = 0;
          // // if (value > 12) value = 12;
          this.numTests = value.toString();
          this.generateConfigs();
        } catch {

        }
      }
    },

    generateConfigs() {
      this.configs = Array.from({ length: this.numTests }, (_, i) => this.createTest(i));
      this.expanded = this.configs.map((_, i) => i);
    },

    generateSampleConfigs() {
      this.configs = [];
      const eachComplexTests = EVAL_NETWORK_TYPE.length * EVAL_LOSS_PERCENTAGE.length * EVAL_NORMAL_AND_PLC.length;

      for (let i = 0; i < NUMBER_OF_SAMPLE_CONFIGS; i += 1) {
        const curComplex = EVAL_COMPLEX[Math.trunc(i / eachComplexTests)];
        const curNetworkType = EVAL_NETWORK_TYPE[(Math.trunc(i/(eachComplexTests/EVAL_NORMAL_AND_PLC.length)) % EVAL_NETWORK_TYPE.length)];
        const networkType = curNetworkType.name;
        let networkData = curNetworkType.data;
        const curLoss = EVAL_LOSS_PERCENTAGE[Math.trunc(i/EVAL_NORMAL_AND_PLC.length)%EVAL_LOSS_PERCENTAGE.length];
        const curUsePlcFlag = EVAL_NORMAL_AND_PLC[(i % EVAL_NORMAL_AND_PLC.length)] === 'normal';

        try {
          let json = JSON.parse(networkData);
          json.down.loss.percentage = curLoss;
          networkData = JSON.stringify(json);
        } catch {}
        // console.log(`Test ${i}\nComplex: ${curComplex}\nPLC Flag: ${curUsePlcFlag}\nNetType: ${networkType}\njson: ${networkData}`)
        this.configs.push(this.createTestWithParams(i, curComplex, curUsePlcFlag, networkType, networkData));
      }

      // this.configs = Array.from({ length: NUMBER_OF_SAMPLE_CONFIGS }, (_, i) => this.createTest(i));
      // this.expanded = this.configs.map((_, i) => i);
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
        complexity: 5,
        taskId: "",
        cancelled: false,
        enableOpusPlc: true,
        result: null,
      };
    },

    createTestWithParams(index, complexity, usePlc, networkType, jsonString) {
      return {
        id: Date.now() + `${complexity}_${usePlc}_${index}`,
        status: TEST_STATUS.PENDING,
        atcConfigs: [
          {
            id: Date.now() + "_" + `${complexity}_${usePlc}_${index}`,
            select: networkType,
            jsonData: jsonString,
            timer: { h: 0, m: 0, s: DEFAULT_ATC_TIMEOUT/1000 },
          }
        ],
        complexity: complexity,
        taskId: "",
        cancelled: false,
        enableOpusPlc: usePlc,
        result: null,
      };
    },

    addTest() {
      // if (this.configs.length >= 12) {
      //   this.openToast("Limit Reached", "You can only add up to 12 tests");
      //   return;
      // }
      const newTest = this.createTest(this.configs.length);
      this.configs.push(newTest);
      this.numTests = (parseInt(this.numTests,10) + 1).toString();
      this.expanded.push(this.configs.length - 1);
    },

    async runTests() {
      for (let i = 0; i < this.configs.length; i++) {
        this.configs[i].taskId = "";
        this.configs[i].result = null;
        this.configs[i].cancelled = false;
        this.configs[i].status = TEST_STATUS.PENDING;
      }
      
      for (let i = 0; i < this.configs.length; i++) {
        while (true && !this.configs[i].cancelled) {
          await this.startAndroidApp(i);
          await new Promise((resolve) => setTimeout(resolve, 2000));

          if (this.configs[i].status === TEST_STATUS.PASS) {
            break;
          } else {
            console.log(`Retrying test ${i}...`);
          }
        }
      }
    },
    
    async deleteTest(index) {
      try {
        // delete current shape
        await deleteShape({ ip: this.deviceIp });
      } catch {}
      this.stopAndroidApp(index);
      
      this.configs.splice(index, 1);
      this.expanded = this.configs.map((_, i) => i);
      this.numTests = (parseInt(this.numTests,10) - 1).toString();
    },

    async stopAndroidApp(index) {
      try {
        // delete current shape
        await deleteShape({ ip: this.deviceIp });
      } catch {}
      try {
        if (this.configs[index].taskId && this.configs[index].taskId.length > 0)
          await stopApp(this.configs[index].taskId);
      } catch {}
      this.configs[index].taskId = "";
      this.configs[index].result = null;
      this.configs[index].cancelled = true;
      this.configs[index].status = TEST_STATUS.PENDING;
    },

    async startAndroidApp(index) {
      this.configs[index].cancelled = false;
      this.configs[index].result = null;
      const test = this.configs[index];
        let totalDelay = 0;
        let atcConfigName = "";
        const timers = test.atcConfigs.map(({ select, timer, jsonData }) => {
          
          let selectString = select.split(".").at(0);

          if (atcConfigName.length == 0) atcConfigName = selectString;
          else atcConfigName += "-" + selectString;

          try {
            let data = JSON.parse(jsonData);
            atcConfigName += `loss${data.down.loss.percentage}`;
          } catch {
            atcConfigName += "loss0";
          }
          const { h, m, s } = timer;
          let delay = (h * 3600 + m * 60 + s) * 1000;
          if (delay <= 0) {
            delay = DEFAULT_ATC_TIMEOUT;
          }
          totalDelay += delay;
          return delay;
        });
        try {
          this.configs[index].status = TEST_STATUS.TESTING;
          this.configs[index].result = null;
          const startAppRes = await runApp({
            deviceId: this.deviceId,
            time: totalDelay / 1000,
            enableOpusPlc: test.enableOpusPlc,
            folderName: atcConfigName,
            complexity: test.complexity
          });

          // console.log("run app with params:", {
          //   deviceId: this.deviceId,
          //   time: totalDelay / 1000,
          //   enableOpusPlc: test.enableOpusPlc,
          //   folderName: atcConfigName,
          //   complexity: test.complexity
          // })
          
          if (!startAppRes || startAppRes.status !== "started") {
            throw new Error("Android App: Cannot start App");
          }

          this.configs[index].taskId = startAppRes.taskId;
          for (let j = 0; j < test.atcConfigs.length; j++) {
            if (this.configs[index].cancelled) return;
            const curConfig = test.atcConfigs[j];

            await applyConfig({
              data: JSON.parse(curConfig.jsonData || "{}"),
              ip: this.deviceIp,
            });
            // wait timer for this config
            await new Promise((resolve) => setTimeout(resolve, timers[j]));
          }

          if (this.configs[index].cancelled) return;
          try {
            await deleteShape({ ip: this.deviceIp });
          } catch {}
          let runAppRes = null;
          
          await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY));
          
          for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            if (this.configs[index].cancelled) return;
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
            const err = new Error("Android App: run fail or missing audio/log files");
            if (runAppRes.result.zrtcLog?.length > 0) {
              err.storeFolder = runAppRes.result.zrtcLog[0]
                                .split("/")
                                .slice(-2, -1)
                                .join("/");
              throw err;
            }
          }

          const numberOfAudioFiles = runAppRes.result.audioFiles.length;
          let flag = false;
          let err;
          for (const audio of runAppRes.result.audioFiles) {
            const duration = await this.getWavDuration(audio)
            if (duration < totalDelay / 1000 - 1) {
              err = new Error(`Android App: Invalid audio file: ${audio}`);
              err.storeFolder = runAppRes.result.zrtcLog[0]
                                .split("/")
                                .slice(-2, -1)
                                .join("/");
              
            } else {
              flag = true
            }
          }

          if (!flag) throw err;

          // Success
          test.result = {
            status: RES_STATUS.SUCCESS,
            audioFiles: runAppRes.result.audioFiles,
            logFile: runAppRes.result.zrtcLog[0],
          };
          test.status = TEST_STATUS.PASS;
          this.configs[index].taskId = "";
        } catch (err) {
          try {
            if (err.storeFolder)
              removeFolder(err.storeFolder);
          } catch {}
          // this.stopAndroidApp(index);
          if (this.configs[index].cancelled) return;
          test.result = {
            status: RES_STATUS.FAILED,
            errorMessage: err.message,
          };
          test.status = TEST_STATUS.FAIL;
        }
    },

    openToast(componentName="", header = "", message = "", timeout = TOAST_TIMEOUT) {
      this.$emit(EVENT_OPEN_TOAST, this.$options.name, header, message, timeout);
    },

    async getWavDuration(url) {
      // fetch only first 44 bytes (WAV header)
      const response = await fetch(url, { headers: { Range: "bytes=0-43" } })
      const header = await response.arrayBuffer()
      const view = new DataView(header)

      // parse WAV header
      const numChannels = view.getUint16(22, true)
      const sampleRate = view.getUint32(24, true)
      const bitsPerSample = view.getUint16(34, true)

      // now fetch the "data" chunk size
      // but safest: fetch file size via HEAD request
      const headResp = await fetch(url, { method: "HEAD" })
      const fileSize = parseInt(headResp.headers.get("Content-Length"))

      // data size = total file size - 44 (header)
      const dataSize = fileSize - 44

      return dataSize / (sampleRate * numChannels * (bitsPerSample / 8))
    }

  },
  watch: {
    
  },
  async mounted() {
    await this.generateConfigs();
  }
};
</script>
