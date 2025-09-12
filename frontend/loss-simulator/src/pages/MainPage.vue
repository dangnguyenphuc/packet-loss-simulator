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
                                v-bind="
                                { 
                                    ...panel.props, 
                                    ...(
                                        panel.component === 'TestInfo' ? 
                                        { deviceId: selectedDevice } : {}
                                    ) 
                                }"
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
import AtcConfigMultiple from '../components/AtcConfig/AtcConfigMultiple.vue';
import {GUIDE_TEXT, EVENT_OPEN_TOAST, TOAST_TIMEOUT} from '../constants/constant'

export default {
    name: 'MainPage',
    components: { DeviceSelector, Guidance, TestInfo, AtcConfigMultiple },
    data() {
        return {
            selectedDevice: '',
            selectedIp: '',
            expanded: [0, 1, 2],
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
                    props: {
                        device: '',
                        ip: '',
                    },
                    events: {
                        EVENT_UPDATE_DEVICE: this.handleFetchDevice,
                        EVENT_UPDATE_DEVICE_IP: this.handleFetchDeviceIp,
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
                    },
                    events: {},
                },
                // 4RD PANEL
                {
                    title: 'Atc Configurations',
                    value: 3,
                    key: 3,
                    class: 'config-container',
                    component: 'AtcConfigMultiple',
                    props: {
                        
                    },
                    events: {},
                },
            ],
        };
    },
    methods: {
        handleFetchDevice(value) {
            this.selectedDevice = value;
        },
        handleFetchDeviceIp(value) {
            this.selectedIp = value;
        },
        openToast(header="", message="", timeout=TOAST_TIMEOUT) {
            this.$emit(EVENT_OPEN_TOAST, header, message, timeout);
        }
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