<template>
    <div>
        <pre>{{content}}</pre>
    </div>
    <div class="mt-5 d-flex flex-row justify-center align-center ga-2">
        <v-btn 
        :color="status === TEST_STATUS.FAIL ? 'red' : 'green'"
        @click="startInstall"
        >
        <template v-slot:prepend>
            <v-progress-circular
            v-if="status === TEST_STATUS.TESTING"
            indeterminate
            size="18"
            width="2"
            />
            <v-icon v-else>{{ statusIcon }}</v-icon>
        </template>

        <span>{{ status === TEST_STATUS.TESTING ? 'Stop' : 'Install' }}</span>
        </v-btn>

            

    </div>
</template>

<script>
import { EVENT_OPEN_TOAST } from '../constants/constant';
import { TEST_STATUS } from '../constants/enums';
import { installApp, stopApp } from '../utils/specific';

export default {
    name: "Guidance",
    props: {
        content: String,
        deviceId: String
    },
    emits: [EVENT_OPEN_TOAST],
    data() {
        return {
            TEST_STATUS,
            status: TEST_STATUS.PENDING,
            taskId: '',
        }
    },
    methods: {
        async startInstall() {

            if (this.status === TEST_STATUS.TESTING) {
                
                this.status = TEST_STATUS.PENDING;
                try {
                    await stopApp(this.taskId)
                } catch (err) {
                }
                this.taskId = "";
                return;
            }

            this.status = TEST_STATUS.TESTING;
            try {
                const result = await installApp(this.deviceId);
                this.taskId = result.taskId;
                try {
                    await stopApp(this.taskId)
                } catch (err) {}
                this.taskId = "";
                this.status = TEST_STATUS.PASS;
            } catch (e) {
                this.$emit(EVENT_OPEN_TOAST, e.message);
                this.status = TEST_STATUS.FAIL;
            }
        }
    },
    computed: {
        statusIcon() {
            if (this.status === TEST_STATUS.PASS) return 'mdi-check-circle';
            if (this.status === TEST_STATUS.FAIL) return 'mdi-close-circle';
            return 'mdi-play-circle'; // Default
        }
    }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap; 
  text-align: left;
}
</style>