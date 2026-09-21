// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Editor from '../views/Editor.vue';
import Create from '../views/Create.vue';
import Guide from '../views/Guide.vue';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/create', name: 'Create', component: Create },
  { path: '/guide', name: 'Guide', component: Guide },
  { path: '/editor/:id', name: 'Editor', component: Editor, props: true },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;