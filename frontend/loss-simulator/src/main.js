import { createApp } from 'vue';
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { createRouter, createWebHistory } from 'vue-router';
import VueApexCharts from 'vue3-apexcharts';
import routes from './router/index.js';
import './style.css';

const vuetify = createVuetify({
    components,
    directives,
    icons: { defaultSet: 'mdi', aliases, sets: { mdi } },
});

const router = createRouter({
    history: createWebHistory(),
    routes,
});

createApp(App)
    .use(vuetify)
    .use(router)
    .use(VueApexCharts)
    .mount('#app');
