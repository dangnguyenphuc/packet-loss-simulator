<template>
    <div class="test-info-container">
        <v-row class="pa-4 d-flex flex-auto ga-2" align="center" justify="center" gap="3">
            <v-col class="d-flex ga-2 flex-column">
                <v-row class="d-flex justify-center align-center">
                    <span>PC Info</span>
                </v-row>
                <v-row
                    v-for="field in infoFieldsPC"
                    :key="field.title"
                    class="d-flex flex-row info-pc-row align-center"
                >
                    <!-- Title column -->
                    <v-col cols="2" class="d-flex justify-start align-center">
                        <span>{{ field.title }}</span>
                    </v-col>

                    <!-- Data column -->
                    <v-col class="d-flex flex-column justify-center">
                        <template v-if="Array.isArray(field.data) && field.data.length > 0">
                            
                            <template v-if="field.title === 'Audio File'">
                                <v-row v-for="(d, i) in field.data" :key="i">
                                   <v-col cols="9">
                                        <v-text-field
                                            :model-value="d.substring(0, d.lastIndexOf('-'))"
                                            readonly
                                            density="compact"
                                        />
                                   </v-col>

                                   <v-col class="d-flex justify-center align-center">
                                       <v-text-field
                                           :model-value="d.substring(d.lastIndexOf('-') + 1)"
                                           readonly
                                           density="compact"
                                       />
                                       <span>
                                           s
                                       </span>
                                   </v-col> 
                                </v-row>
                            </template>
                            <template v-else>
                                <v-text-field
                                    v-for="(d, i) in field.data"
                                    :key="i"
                                    :model-value="d"
                                    readonly
                                    density="compact"
                                />
                            </template>
                        </template>
                        <template v-else>
                            <v-text-field
                                :model-value="field.data"
                                readonly
                                density="compact"
                            />
                        </template>
                    </v-col>
                </v-row>
            </v-col>

            <v-col class="d-flex flex-column ga-2">
                <v-row class="d-flex justify-center align-center">
                    <span>Android Info</span>
                </v-row>
                <v-row
                    v-for="field in infoFieldsAndroid"
                    :key="field.title"
                    class="d-flex flex-row info-row align-center"
                >
                    <!-- Title column -->
                    <v-col cols="2" class="d-flex justify-start align-center">
                        <span>{{ field.title }}</span>
                    </v-col>

                    <!-- Data column -->
                    <v-col class="d-flex flex-column gap-2">
                        <template v-if="Array.isArray(field.data) && field.data.length > 0">
                            <v-text-field
                                v-for="(d, i) in field.data"
                                :key="i"
                                :model-value="d"
                                readonly
                                density="compact"
                            />
                        </template>
                        <template v-else>
                            <v-text-field
                                :model-value="field.data"
                                readonly
                                density="compact"
                            />
                        </template>
                    </v-col>
                </v-row>
            </v-col>
        </v-row>
    </div>
</template>

<script>
import { fetchInfo } from '../utils/specific';

export default {
    name: 'TestInfo',
    props: {
        deviceId: {
            type: String,
            default: '',
        },
    },
    data() {
        return {
            infoFieldsPC: [
                {
                    title: 'Audio File',
                    data: [],
                },
                {
                    title: 'Record Folder',
                    data: '',
                },
            ],
            infoFieldsAndroid: [
                {
                    title: 'Uploaded Audio Folder',
                    data: '',
                },
                {
                    title: 'Record Audio Folder',
                    data: '',
                },
                {
                    title: 'Histogram Folder',
                    data: '',
                },
                {
                    title: 'App Package',
                    data: '',
                },
                {
                    title: 'Target Activities',
                    data: [],
                },
            ],
        };
    },
    methods: {
        async fetchTestInfo() {
            if (!this.deviceId) return;
            try {
                const info = await fetchInfo(this.deviceId);
                this.infoFieldsPC[0].data = info.pc.audio;
                this.infoFieldsPC[1].data = info.pc.recordFolder;
                this.infoFieldsAndroid[0].data = info.android.uploadAudioFolder;
                this.infoFieldsAndroid[1].data = info.android.recordAudioFolder;
                this.infoFieldsAndroid[2].data = info.android.histogramStorePath;
                this.infoFieldsAndroid[3].data = info.android.appPackage;
                this.infoFieldsAndroid[4].data = info.android.activity;
            } catch (err) {
                console.error('Error fetching test info:', err.message);
            }
        },
    },
    watch: {
        deviceId(newVal) {
            this.fetchTestInfo();
        },
    },
    mounted() {
        this.fetchTestInfo();
    },
};
</script>

<style scoped>
.info-row {
    background-color: rgb(227, 198, 255);
}
.info-pc-row {
    background-color: rgb(238, 223, 232);
}
</style>