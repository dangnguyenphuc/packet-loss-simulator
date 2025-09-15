<template>
    <v-container class="main-container">
        <v-row justify="center">
            <v-col>
                <h1>Hello, User!</h1>
            </v-col>
        </v-row>
        <v-expansion-panels v-model="expanded" multiple>
            <v-expansion-panel
                v-for="panel in panels"
                :key="panel.key"
                :value="panel.value"
                :class="panel.class"
            >
                <div v-if="panel.key < 10 || (selectedDevice && selectedIp)">
                    <v-expansion-panel-title>
                        <span class="title">{{ panel.title }}</span>
                    </v-expansion-panel-title>
                    <v-expansion-panel-text>
                        <component
                            :is="panel.component"
                            @open:Toast="openToast"
                            v-bind="panel.props"
                            v-on="panel.events"
                        />
                    </v-expansion-panel-text>
                </div>
            </v-expansion-panel>
        </v-expansion-panels>
    </v-container>
</template>

<script>
import DeviceSelector from '../components/DeviceSelector.vue';
import Guidance from '../components/Guidance.vue';
import TestInfo from '../components/TestInfo.vue';
import ConfigAndRun from '../components/AtcConfig/ConfigAndRun.vue';
import {
    GUIDE_TEXT, 
    EVENT_OPEN_TOAST, 
    TOAST_TIMEOUT,
    EVENT_UPDATE_DEVICE,
    EVENT_UPDATE_DEVICE_IP,
    EVENT_FETCH_DEVICE
} from '../constants/constant';
import { fetchJsons } from '../utils/specific';

export default {
    name: 'MainPage',
    components: { DeviceSelector, Guidance, TestInfo, ConfigAndRun },
    data() {
        return {
            selectedDevice: '',
            selectedIp: '',
            expanded: [1, 2, 3],
            panels: [
                // FIRST PANEL
                {
                    title: 'How to use',
                    value: 0,
                    key: 0,
                    class: 'intro',
                    component: 'Guidance',
                    props: {
                        content: GUIDE_TEXT,
                    },
                    events: {},
                },
                // SECOND PANEL
                {
                    title: 'Device Selector',
                    value: 1,
                    key: 1,
                    class: 'device-selector',
                    component: 'DeviceSelector',
                    props: {},
                    events: {
                        [EVENT_UPDATE_DEVICE]: this.handleFetchDevice,
                        [EVENT_UPDATE_DEVICE_IP]: this.handleFetchDeviceIp,
                        [EVENT_FETCH_DEVICE]: this.handleCompletedFetchDevice
                    },
                },
                // 3RD PANEL
                {
                    title: 'Auto test information',
                    value: 2,
                    key: 2,
                    class: 'test-info',
                    component: 'TestInfo',
                    props: {
                        display: false,
                        deviceId: '',
                    },
                    events: {},
                },
                // 4TH PANEL
                {
                    title: 'Config ATC and Run Tests',
                    value: 3,
                    key: 3,
                    class: 'config-container',
                    component: 'ConfigAndRun',
                    props: {
                        display: false,
                        atcConfigs: [],
                        deviceId: "",
                        deviceIp: ""
                    },
                    events: {},
                }
            ],
        };
    },
    methods: {
        handleFetchDevice(value) {
            this.selectedDevice = value;
            this.panels[2].props.deviceId = value;
        },
        handleFetchDeviceIp(value) {
            this.selectedIp = value;
        },
        async handleCompletedFetchDevice(value) {
            // display all other panels
            for (let i = 2; i < this.panels.length; i+=1) {
                this.panels[i].props.display = value;
            }

            // fetch defined ATC Configs
            try {
                const atcConfigSelections = await fetchJsons();
                if (!atcConfigSelections.hasOwnProperty("files")) throw new Error("Response ATC Configs doesn't have \"files\" field")
                this.panels[3].props.atcConfigs = atcConfigSelections.files;
                this.panels[3].props.deviceId = this.selectedDevice;
                this.panels[3].props.deviceIp = this.selectedIp;
            } catch (err) {
                openToast("Error Getting ATC Configs file", err.message);
            }
        },
        openToast(header = "", message = "", timeout = TOAST_TIMEOUT) {
            this.$emit(EVENT_OPEN_TOAST, header, message, timeout);
        },
    },
};
</script>

<style scoped>
.main-container {
    width: 1200px;
}

@media (max-width: 767) {
    .main-container {
        width: 600px;
    }
}

@media (max-width: 566) {
    .main-container {
        width: 350px;
    }
}
</style>