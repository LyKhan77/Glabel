import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'
import Workspace from './views/Workspace.vue'
import VisionJourney from './views/VisionJourney.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/playgrounds', component: Workspace }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

createApp(App).use(router).mount('#app')
