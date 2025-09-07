<template>
    <v-container class="d-flex flex-column ga-3">
        <v-row justify="center">
            <v-col>
                <h1>Hello, {{ name }}!</h1>
            </v-col>
        </v-row>

        <v-row class="intro" v-ripple @click="introExpanded = !introExpanded">
            <v-col md="3" cols="12" class="title d-flex align-center justify-center">
                <span>How to use</span>
            </v-col>
            <v-col cols="12" md="9">
                <v-expand-transition>
                    <div v-show="introExpanded" class="bg-light pa-4">
                        <pre>
+ Fix90: Fixed 90% packet loss rate
+ Dynamic: Loss rate varies over time (each ... second)
+ IncreaseOnly: Same as Dynamic but loss rate always increase</pre>
                    </div>
                </v-expand-transition>
            </v-col>
        </v-row>

        <template v-if="name === 'Stranger'">
            <v-row>
                <v-col>
                    <h2>You don't have any permission, please call for help</h2>
                </v-col>
            </v-row>
        </template>
        <template v-else>
            <device-selector
                v-model:device="selectedDevice"
                v-model:ip="selectedIp"
                @fetch-devices="fetchDevices"
                @delete-config="deleteConfig"
            />
            <v-row v-if="selectedIp" class="mt-3">
                <v-col>
                    <timer v-model:hours="hours" v-model:minutes="minutes" v-model:seconds="seconds" />
                    <v-row class="config-container">
                        <v-col md="6" cols="12" class="default-config-json pa-4">
                            <json-editor
                                v-model:json="jsonContent"
                                v-model:selected-file="selectedJsonFile"
                                :files="files"
                                @apply-config="applyJsonConfig"
                            />
                        </v-col>
                        <v-col md="6" cols="12" class="defined-loss-strategy pa-4">
                            <strategy-selector
                                v-model:selected-strategy="selectedStrategy"
                                v-model:loss-value="lossValue"
                                v-model:cycle-seconds="cycleSeconds"
                                :strategies="strategies"
                                @apply-strategy="applyStrategy"
                            />
                        </v-col>
                    </v-row>
                </v-col>
            </v-row>
        </template>
    </v-container>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import { fetchDevices, fetchDeviceIp, applyConfig, deleteShape, convertTimerToMs, postShape } from '../utils/specific.js';
import DeviceSelector from '../components/DeviceSelector.vue';
import Timer from '../components/Timer.vue';
import JsonEditor from '../components/JsonEditor.vue';
import StrategySelector from '../components/StrategySelector.vue';

export default {
    name: 'MainPage',
    components: { DeviceSelector, Timer, JsonEditor, StrategySelector },
    setup() {
        // Mock data (replace with API calls if needed)
        const name = ref('User'); // Replace with actual user data
        const files = ref(['config1.json', 'config2.json']); // Mock JSON files
        const strategies = ref(['Fix90', 'Dynamic', 'IncreaseOnly']); // Mock strategies
        const selectedDevice = ref('');
        const selectedIp = ref('');
        const hours = ref(0);
        const minutes = ref(0);
        const seconds = ref(0);
        const selectedJsonFile = ref('');
        const jsonContent = ref('');
        const selectedStrategy = ref('');
        const lossValue = ref('');
        const cycleSeconds = ref(5);
        const introExpanded = ref(false);
        let countDownInterval = null;
        let cycleInterval = null;
        let previousIp = ref('');

        const setTimerValue = (value) => {
            const totalSeconds = Math.floor(value / 1000);
            seconds.value = totalSeconds % 60;
            minutes.value = Math.floor((totalSeconds % 3600) / 60);
            hours.value = Math.floor(totalSeconds / 3600);
        };

        const resetTimer = async () => {
            if (countDownInterval) clearInterval(countDownInterval);
            if (cycleInterval) clearInterval(cycleInterval);
            try {
                if (previousIp.value) {
                    await deleteShape({ ip: previousIp.value });
                }
            } finally {
                countDownInterval = null;
                hours.value = 0;
                minutes.value = 0;
                seconds.value = 0;
                previousIp.value = '';
                alert('[TIMER] DELETED CONFIG');
            }
        };

        const countDown = (timeLeft) => {
            if (timeLeft <= 0) return;
            if (countDownInterval) clearInterval(countDownInterval);
            countDownInterval = setInterval(() => {
                timeLeft -= 1000;
                setTimerValue(timeLeft);
                if (timeLeft <= 0) resetTimer();
            }, 1000);
        };

        const fetchDevices = async () => {
            try {
                const { data } = await fetchDevices();
                selectedDevice.value = data[0] || '';
                if (selectedDevice.value) fetchDeviceIps();
            } catch (err) {
                // alert('[GET] Devices error');
            }
        };

        const fetchDeviceIps = async () => {
            try {
                const { data } = await fetchDeviceIp(selectedDevice.value);
                const validIps = data.filter(ip => ip.ip.startsWith('10.42'));
                selectedIp.value = validIps[0]?.ip || '';
            } catch (err) {
                alert(`[GET] Ips error: ${err.message}`);
            }
        };

        const deleteConfig = async () => {
            if (!confirm('Are you sure you want to delete this config?')) return;
            try {
                await deleteShape({ ip: selectedIp.value });
                alert('Deleted successfully!');
                resetTimer();
            } catch (err) {
                alert(`Error deleting config: ${err.message}`);
            }
        };

        const applyJsonConfig = async () => {
            try {
                const payload = {
                    ip: selectedIp.value,
                    data: JSON.parse(jsonContent.value),
                };
                const timerValue = convertTimerToMs(hours.value, minutes.value, seconds.value);
                await applyConfig(payload);
                countDown(timerValue);
                previousIp.value = selectedIp.value;
                selectedStrategy.value = '';
            } catch (err) {
                alert(`Error: ${err.message}`);
            }
        };

        const applyStrategy = async () => {
            try {
                const payload = {
                    ip: selectedIp.value,
                    strategy: selectedStrategy.value,
                };
                const timerValue = convertTimerToMs(hours.value, minutes.value, seconds.value);
                const resp = await applyConfig(payload);
                countDown(timerValue);
                previousIp.value = selectedIp.value;
                selectedJsonFile.value = '';
                lossValue.value = resp.loss || '';
                if (cycleInterval) clearInterval(cycleInterval);
                if (!selectedStrategy.value.startsWith('fix') && cycleSeconds.value > 0) {
                    cycleInterval = setInterval(async () => {
                        try {
                            const resp = await postShape(payload);
                            lossValue.value = resp.loss || '';
                            selectedJsonFile.value = '';
                        } catch (e) {
                            clearInterval(cycleInterval);
                            cycleInterval = null;
                            lossValue.value = '';
                            alert(`Error: ${e.message}`);
                        }
                    }, cycleSeconds.value * 1000);
                }
            } catch (err) {
                alert(`Error: ${err.message}`);
            }
        };

        watch(selectedDevice, fetchDeviceIps);

        onMounted(fetchDevices);

        return {
            name,
            files,
            strategies,
            selectedDevice,
            selectedIp,
            hours,
            minutes,
            seconds,
            selectedJsonFile,
            jsonContent,
            selectedStrategy,
            lossValue,
            cycleSeconds,
            introExpanded,
            fetchDevices,
            deleteConfig,
            applyJsonConfig,
            applyStrategy,
        };
    },
};
</script>