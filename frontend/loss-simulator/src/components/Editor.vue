<template>
    <v-card>
        <v-card-text>
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
import { EditorView } from '@codemirror/view';

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
                this.lang === "json" ? json() : null,
                EditorView.lineWrapping
            ],
        }
    },
    methods: {

    },

    watch: {
        code(newValue) {
            this.$emit(EVENT_UPDATE_MODEL, newValue);
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
  height: 300px;
}

.editor {
    width: 100%;
}

</style>