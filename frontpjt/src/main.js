// frontpjt/src/main.js
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Bootstrap CSS 및 JS 가져오기
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css' // Bootstrap CSS
import 'bootstrap-icons/font/bootstrap-icons.css' // ★ Bootstrap Icons


const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')