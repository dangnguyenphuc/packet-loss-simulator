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
                    <div v-if="panel.key < 2 || (selectedDevice && selectedIp)">
                        <v-expansion-panel-title>
                            <span class="title">{{ panel.title }}</span>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                            <component
                                :is="panel.component"
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
import {GUIDE_TEXT} from '../constants/constant'

export default {
    name: 'MainPage',
    components: { DeviceSelector, Guidance },
    data() {
        return {
            selectedDevice: '',
            selectedIp: '',
            expanded: [0, 1],
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
                        'update:device': this.handleFetchDevice,
                        'update:deviceIp': this.handleFetchDeviceIp,
                    },
                },

                // 3RD PANEL
                {
                    title: 'Path Selector',
                    value: 2,
                    key: 2,
                    class: 'intro',
                    component: 'Guidance',
                    props: {
                        content: `+ Fix90: Fixed 90% packet loss rate
+ Dynamic: Loss rate varies over time (each ... second)
+ IncreaseOnly: Same as Dynamic but loss rate always increase`,
                    },
                    events: {},
                },
                // 4RD PANEL
                {
                    title: 'How to use',
                    value: 3,
                    key: 3,
                    class: 'intro',
                    component: 'Guidance',
                    props: {
                        content: GUIDE_TEXT,
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
    },
};
</script>

<style scoped>
.main-container {
    width: 1000px;
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