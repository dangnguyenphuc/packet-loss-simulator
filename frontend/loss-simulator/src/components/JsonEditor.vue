<template>
    <v-row class="d-flex flex-column align-center ga-3">
        <v-col cols="12" class="title">
            <span>Default Config JSON</span>
        </v-col>
        <v-col cols="12" class="d-flex align-center ga-3">
            <v-select
                label="Choose a config"
                v-model="selectedFile"
                :items="[{ value: '', title: '-- Select a config --' }, ...files.map(f => ({ value: f, title: f.replace('.json', '') }))]"
                @update:modelValue="fetchJson"
            ></v-select>
        </v-col>
        <v-col cols="12" v-show="selectedFile">
            <div ref="editor" style="height: 300px; border: 1px solid #ccc;"></div>
            <v-btn color="primary" @click="$emit('apply-config')" :class="{ 'applied-btn': isApplied }"> {{ isApplied ? 'Applied' : 'Apply' }} </v-btn>
        </v-col>
    </v-row>
</template>

<script>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { fetchJson } from '../utils/specific.js';
import * as monaco from 'monaco-editor';

export default {
    name: 'JsonEditor',
    props: {
        json: String,
        selectedFile: String,
        files: Array,
    },
    emits: ['update:json', 'update:selected-file', 'apply-config'],
    setup(props, { emit }) {
        const editor = ref(null);
        const jsonContent = ref(props.json);
        const selectedFile = ref(props.selectedFile);
        const isApplied = ref(false);
        let monacoInstance = null;

        const fetchJson = async () => {
            if (!selectedFile.value) {
                jsonContent.value = '';
                emit('update:json', '');
                if (monacoInstance) monacoInstance.setValue('');
                return;
            }
            try {
                const data = await fetchJson(selectedFile.value);
                const content = JSON.stringify(data.data.content || data.data, null, 2);
                jsonContent.value = content;
                if (monacoInstance) monacoInstance.setValue(content);
                emit('update:json', content);
                isApplied.value = false;
            } catch (err) {
                jsonContent.value = `// ${err.message}`;
                if (monacoInstance) monacoInstance.setValue(jsonContent.value);
                emit('update:json', jsonContent.value);
            }
        };

        watch(selectedFile, (newVal) => {
            emit('update:selected-file', newVal);
            fetchJson();
        });

        watch(() => props.json, (newVal) => {
            if (newVal !== jsonContent.value) {
                jsonContent.value = newVal;
                if (monacoInstance) monacoInstance.setValue(newVal);
            }
        });

        onMounted(() => {
            monacoInstance = monaco.editor.create(editor.value, {
                value: jsonContent.value || '',
                language: 'json',
                theme: 'vs-dark',
                automaticLayout: true,
                lineNumbers: 'on',
            });

            monacoInstance.onDidChangeModelContent(() => {
                jsonContent.value = monacoInstance.getValue();
                emit('update:json', jsonContent.value);
                isApplied.value = false;
            });
        });

        onBeforeUnmount(() => {
            if (monacoInstance) {
                monacoInstance.dispose();
            }
        });

        return { editor, selectedFile, isApplied };
    },
};
</script>

<style scoped>
.applied-btn {
    background-color: green !important;
    color: white !important;
}
</style>