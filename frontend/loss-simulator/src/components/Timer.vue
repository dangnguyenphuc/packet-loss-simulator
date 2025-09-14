<template>
    <v-row>
        <v-col cols="12" class="d-flex align-center justify-center ga-3">
            <v-text-field
                type="number"
                v-model="hour"
                :min="0"
                class="timer-input-field"
                hide-details
            ></v-text-field>
            <span>:</span>
            <v-text-field
                type="number"
                v-model="minute"
                :min="0"
                :max="59"
                hide-details
                class="timer-input-field"
            ></v-text-field>
            <span>:</span>
            <v-text-field
                type="number"
                v-model="second"
                :min="0"
                :max="59"
                hide-details
                class="timer-input-field"
            ></v-text-field>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';

export default {
    name: 'Timer',
    props: {
        hour: Number,
        minute: Number,
        second: Number,
    },
    emits: ['update:hour', 'update:minute', 'update:second'],
    setup(props, { emit }) {
        const hour = ref(props.hour);
        const minute = ref(props.minute);
        const second = ref(props.second);

        watch(hour, (newVal) => emit('update:hour', parseInt(newVal) || 0));
        watch(minute, (newVal) => emit('update:minute', parseInt(newVal) || 0));
        watch(second, (newVal) => emit('update:second', parseInt(newVal) || 0));

        return { hour, minute, second };
    },
};
</script>

<style scoped>
.timer-input-field {
    width: 60px;
}
</style>