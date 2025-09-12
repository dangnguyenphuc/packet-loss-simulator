<template>
    <v-container>
        <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center pa-0">
            <v-col class="d-flex justify-center align-center pa-0" >
                <v-select v-model="row.select1" :items="selectorOptions" label="Select 1"></v-select>
            </v-col>
            <v-col>

            </v-col>

            <!-- Timer (H, M, S) -->
            <v-col class="d-flex justify-center align-center pa-0">
                <v-row class="d-flex justify-center align-center pa-0 ga-1">
                    <v-col class="d-flex justify-center align-center pa-0">
                        <v-text-field v-model.number="row.timer.h" label="H" type="number" min="0"></v-text-field>
                    </v-col>
                    <v-col class="d-flex justify-center align-center pa-0">
                        <v-text-field v-model.number="row.timer.m" label="M" type="number" min="0"
                            max="59"></v-text-field>
                    </v-col>
                    <v-col class="d-flex justify-center align-center pa-0">
                        <v-text-field v-model.number="row.timer.s" label="S" type="number" min="0"
                            max="59"></v-text-field>
                    </v-col>
                </v-row>
            </v-col>

            <!-- Delete Button -->
            <v-col cols="1" class="d-flex justify-center align-center">
                <v-btn color="red" @click="deleteRow(index)" icon="mdi-delete" density="compact" ></v-btn>
            </v-col>
        </v-row>

        <!-- Control Buttons -->
        <v-row class="d-flex justify-center align-center pa-0 ga-3">
            <v-btn density="compact" icon="mdi-plus" @click="addRow"></v-btn>
            <v-btn density="compact" icon="mdi-undo" @click="resetRows" :disabled="disableApply"></v-btn>
            <v-btn density="compact" prepend-icon="mdi-check" @click="applyRows" :disabled="disableApply">Apply</v-btn>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: "AtcConfig",
    data() {
        return {
            rows: [
                {
                    id: Date.now(),
                    select1: null,
                    jsonData: null,
                    timer: { h: 0, m: 0, s: 0 },
                },
            ],
            selectorOptions: [],
        };
    },
    methods: {
        addRow() {
            this.rows.push({
                id: Date.now(),
                select1: null,
                jsonData: null,
                timer: { h: 0, m: 0, s: 0 },
            });
        },
        deleteRow(index) {
            this.rows.splice(index, 1);
        },
        resetRows() {
            this.rows = [];
        },
        applyRows() {
            console.log("Applying rows:", this.rows);
        },
    },
    computed: {
        disableApply() {
            return this.rows.length === 0;
        }
    }
};
</script>
