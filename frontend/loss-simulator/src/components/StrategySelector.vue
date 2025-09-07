<template>
    <v-row class="d-flex flex-column align-center ga-3">
        <v-col cols="12" class="title">
            <span>Defined Loss Strategies</span>
        </v-col>
        <v-col cols="12">
            <v-select
                label="Choose a strategy"
                v-model="selectedStrategy"
                :items="[{ value: '', title: '-- Select a strategy --' }, ...strategies.map(s => ({ value: s, title: s.replace('.json', '') }))]"
            ></v-select>
        </v-col>
        <v-col v-if="selectedStrategy && !selectedStrategy.startsWith('fix')" class="d-flex flex-column align-center ga-3">
            <v-row justify="center">
                <v-col cols="12" class="d-flex justify-center align-center">
                    <span>Loss Percentage: </span>
                    <v-text-field
                        v-model="lossValue"
                        type="number"
                        readonly
                        disabled
                        style="width: 100px"
                    ></v-text-field>
                    <span>%</span>
                </v-col>
                <v-col cols="12" class="d-flex justify-center align-center">
                    <span>Change every </span>
                    <v-text-field
                        v-model="cycleSeconds"
                        type="number"
                        :min="0"
                        style="width: 60px"
                    ></v-text-field>
                    <span>s</span>
                </v-col>
            </v-row>
            <v-btn color="primary" @click="$emit('apply-strategy')" :disabled="!selectedStrategy">Apply</v-btn>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch } from 'vue';

export default {
    name: 'StrategySelector',
    props: {
        selectedStrategy: String,
        lossValue: String,
        cycleSeconds: Number,
        strategies: Array,
    },
    emits: ['update:selected-strategy', 'update:loss-value', 'update:cycle-seconds', 'apply-strategy'],
    setup(props, { emit }) {
        const selectedStrategy = ref(props.selectedStrategy);
        const lossValue = ref(props.lossValue);
        const cycleSeconds = ref(props.cycleSeconds);

        watch(selectedStrategy, (newVal) => emit('update:selected-strategy', newVal));
        watch(lossValue, (newVal) => emit('update:loss-value', newVal));
        watch(cycleSeconds, (newVal) => emit('update:cycle-seconds', parseInt(newVal) || 0));

        return { selectedStrategy, lossValue, cycleSeconds };
    },
};
</script>