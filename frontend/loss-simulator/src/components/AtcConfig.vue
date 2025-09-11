<template>
    <v-container>
        <v-row v-for="(row, index) in rows" :key="row.id" class="d-flex justify-center align-center" align="center">
            <v-col cols="3">
                <v-select v-model="row.select1" :items="selectorOptions1" label="Select 1"></v-select>
            </v-col>
            <v-col cols="3">
                <v-select v-model="row.select2" :items="selectorOptions2" label="Select 2"></v-select>
            </v-col>

            <!-- Timer (H, M, S) -->
            <v-col cols="4">
                <v-row>
                    <v-col cols="4">
                        <v-text-field v-model.number="row.timer.h" label="H" type="number" min="0"></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field v-model.number="row.timer.m" label="M" type="number" min="0"
                            max="59"></v-text-field>
                    </v-col>
                    <v-col cols="4">
                        <v-text-field v-model.number="row.timer.s" label="S" type="number" min="0"
                            max="59"></v-text-field>
                    </v-col>
                </v-row>
            </v-col>

            <!-- Delete Button -->
            <v-col cols="2" class="d-flex justify-center align-center">
                <v-btn color="red" @click="deleteRow(index)" small>Delete</v-btn>
            </v-col>
        </v-row>

        <!-- Control Buttons -->
        <v-row class="mt-6" justify="center" align="center" dense>
            <v-btn color="primary" class="mr-2" @click="addRow">Add Row</v-btn>
            <v-btn color="success" class="mr-2" @click="applyRows" :disabled="disableApply">Apply</v-btn>
            <v-btn color="grey" @click="resetRows" :disabled="disableApply">Reset</v-btn>
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
                    select2: null,
                    timer: { h: 0, m: 0, s: 0 },
                },
            ],
            selectorOptions1: ["Option A1", "Option A2", "Option A3"],
            selectorOptions2: ["Option B1", "Option B2", "Option B3"],
        };
    },
    methods: {
        addRow() {
            this.rows.push({
                id: Date.now(),
                select1: null,
                select2: null,
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
