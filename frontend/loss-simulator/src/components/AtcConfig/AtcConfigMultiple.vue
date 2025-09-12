<template>
  <v-container>
    <!-- Input N -->
    <v-row class="mb-4">
      <v-col cols="12" md="4">
        <v-text-field
          v-model="numTests"
          type="text"
          label="Number of Tests (0 - 10)"
          @input="validateNumTests"
        />
      </v-col>
    </v-row>

    <!-- Expansion Panels -->
    <v-expansion-panels v-model="expanded" multiple>
      <v-expansion-panel
        v-for="(test, index) in configs"
        :key="index"
        :value="index"
      >
        <v-expansion-panel-title>
          <v-row class="w-100 d-flex align-center">
            <v-col cols="6"> Test #{{ index + 1 }} </v-col>
            <v-col cols="6" class="d-flex justify-end align-center">
              <v-progress-circular
                v-if="test.status === 'testing'"
                indeterminate
                color="primary"
                size="20"
                width="2"
              />
              <v-icon v-else-if="test.status === 'pass'" color="green">
                mdi-check-circle
              </v-icon>
              <v-icon v-else-if="test.status === 'fail'" color="red">
                mdi-close-circle
              </v-icon>
              <v-icon v-else-if="test.status === 'pending'" color="grey">
                mdi-help-circle
              </v-icon>
            </v-col>
          </v-row>
        </v-expansion-panel-title>

        <v-expansion-panel-text>
          <AtcConfig />
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <!-- Control Buttons -->
    <v-row class="mt-4">
      <v-col>
        <v-btn color="primary" @click="runTestsSequential">Run Sequential</v-btn>
        <v-btn color="secondary" class="ml-2" @click="runTestsParallel">Run Parallel</v-btn>
        <v-btn color="red" variant="tonal" class="ml-2" @click="resetTests">
          Reset
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import AtcConfig from "./AtcConfig.vue";

export default {
  name: "AtcConfigMultiple",
  components: { AtcConfig },
  data() {
    return {
      numTests: "1", // keep as string because of text input
      configs: [],
      expanded: [],
    };
  },
  methods: {
    validateNumTests() {
      let value = parseInt(this.nuests, 10);
      if (isNaN(value)) value = 0;
      if (value < 0) value = 0;
      if (value > 10) value = 10;

      this.numTests = value.toString();
      this.generateConfigs();
    },

    generateConfigs() {
      const count = parseInt(this.numTests, 10) || 0;
      this.configs = Array.from({ length: count }, () => ({
        status: "pending", // pending | testing | pass | fail
      }));
      this.expanded = this.configs.map((_, i) => i);
    },

    async runTestsSequential() {
      for (let i = 0; i < this.configs.length; i++) {
        this.configs[i] = { ...this.configs[i], status: "testing" };
        await new Promise((resolve) => setTimeout(resolve, 2000));
        const didPass = Math.random() > 0.4;
        this.configs[i] = { ...this.configs[i], status: didPass ? "pass" : "fail" };
      }
    },

    runTestsParallel() {
      this.configs.forEach((_, i) => {
        this.configs[i] = { ...this.configs[i], status: "testing" };
        setTimeout(() => {
          const didPass = Math.random() > 0.4;
          this.configs[i] = { ...this.configs[i], status: didPass ? "pass" : "fail" };
        }, 2000 + i * 500);
      });
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
