<template>
    <v-row class="pa-4" align="center" justify="center" gap="3">
        <v-col>
            <v-row class="d-flex justify-center align-center">
                <span>PC Info</span>
            </v-row>
            <v-row 
            v-for="field in infoFieldsPC"
            :key="field.title"
            class="d-flex flex-row info-pc-row align-center"
            >
            <!-- Title column -->
            <v-col cols="3" class="d-flex justify-start align-center">
                <span>{{ field.title }}</span>
            </v-col>

            <!-- Data column -->
            <v-col class="d-flex flex-column justify-center">
                <template v-if="Array.isArray(field.data)">
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

         <v-col>
            <v-row class="d-flex justify-center align-center">
                <span>Android Info</span>
            </v-row>
            <v-row 
            v-for="field in infoFieldsAndroid"
            :key="field.title"
            class="d-flex flex-row info-row align-center"
            >
            <!-- Title column -->
            <v-col cols="3" class="d-flex justify-start align-center">
                <span>{{ field.title }}</span>
            </v-col>

            <!-- Data column -->
            <v-col class="d-flex flex-column gap-2">
                <template v-if="Array.isArray(field.data)">
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
</template>

<script>
import { fetchInfo } from '../utils/specific';

export default {
    name: 'TestInfo',
    
    data() {
        return {
            infoFieldsPC: [
                {
                    title: "Audio File",
                    data: [""]
                },
                {
                    title: "Record Folder",
                    data: ""
                },
            ],
            infoFieldsAndroid: [
                {
                    title: "Uploaded Audio Folder",
                    data: ""
                },
                {
                    title: "Record Audio Folder",
                    data: ""
                },
                {
                    title: "Histogram Folder",
                    data: ""
                }
            ]
        };
    },
    methods: {
    },
    watch: {
        
    },
    async created() {
        try {
            const info = await fetchInfo();
            // console.log(audioFiles)
            this.infoFieldsPC[0].data = info.pc.audio;
            this.infoFieldsPC[1].data = info.pc.recordFolder;

            this.infoFieldsAndroid[0].data = info.android.uploadAudioFolder;
            this.infoFieldsAndroid[1].data = info.android.recordAudioFoler;
            this.infoFieldsAndroid[2].data = info.android.histogramStorePath;
        }
        catch {
            console.log(err.message);
        }
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