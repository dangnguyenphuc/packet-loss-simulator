import { createApp } from 'vue';
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { createRouter, createWebHistory } from 'vue-router';
import routes from './router/index.js';
import './style.css';

// Vuetify setup
const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: { mdi },
    },
});

// Router setup
const router = createRouter({
    history: createWebHistory(),
    routes,
});

const app = createApp(App);
app.use(vuetify);
app.use(router);
app.mount('#app');