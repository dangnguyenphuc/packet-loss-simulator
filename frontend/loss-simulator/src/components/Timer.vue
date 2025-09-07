<template>
    <v-row class="timer-container pa-4">
        <v-col cols="12" class="title">
            <span>Timer</span>
        </v-col>
        <v-col cols="12" class="d-flex align-center justify-center ga-3">
            <span>Time to apply config:</span>
            <v-text-field
                type="number"
                v-model="hours"
                :min="0"
                style="width: 60px"
            ></v-text-field>
            <span>:</span>
            <v-text-field
                type="number"
                v-model="minutes"
                :min="0"
                :max="59"
                style="width: 60px"
            ></v-text-field>
            <span>:</span>
            <v-text-field
                type="number"
                v-model="seconds"
                :min="0"
                :max="59"
                style="width: 60px"
            ></v-text-field>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';

export default {
    name: 'Timer',
    props: {
        hours: Number,
        minutes: Number,
        seconds: Number,
    },
    emits: ['update:hours', 'update:minutes', 'update:seconds'],
    setup(props, { emit }) {
        const hours = ref(props.hours);
        const minutes = ref(props.minutes);
        const seconds = ref(props.seconds);

        watch(hours, (newVal) => emit('update:hours', parseInt(newVal) || 0));
        watch(minutes, (newVal) => emit('update:minutes', parseInt(newVal) || 0));
        watch(seconds, (newVal) => emit('update:seconds', parseInt(newVal) || 0));

        return { hours, minutes, seconds };
    },
};
</script>