import { createRouter, createWebHistory } from 'vue-router';
import MainPage from '../pages/MainPage.vue';

const routes = [
    {
        path: '/',
        name: 'MainPage',
        component: MainPage,
    },
];

export default routes;