<template>
    <v-card>
        <v-card-text >
            <codemirror
                v-model="code"
                class="editor"
                :extensions="extensions"
            />
        </v-card-text>
    </v-card>
</template>

<script>
import { Codemirror } from 'vue-codemirror';
import { json } from '@codemirror/lang-json';
import { EVENT_UPDATE_MODEL } from '../constants/constant'

export default {
    name: 'Editor',
    components: { Codemirror },
    props: {
        lang: {
            type: String,
            required: false,
            default: "json",
        },
        modelValue: {
            type: String,
            required: true, // Or false if you want a default
        },
    },
    data() {
        return {
            code: this.modelValue,
            extensions: [
                this.lang === "json" ? json() : null,  // Fixed: Compare to string "json"
            ],
        }
    },
    methods: {

    },

    watch: {
        code(newValue) {
            this.$emit('update:modelValue', newValue);
        },
        modelValue(newValue) {
            if (newValue !== this.code) {
                this.code = newValue;
            }
        }
    },
}
</script>

<style scoped>
:deep(.cm-editor) {
  text-align: left !important;
  display: block !important;
}

.editor {
    height: 100%;
    width: 100%;
}
</style>