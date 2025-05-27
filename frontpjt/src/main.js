// front/src/main.js
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Bootstrap CSS 및 JS 가져오기
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap' // ★★★ JS 번들 대신 기본 bootstrap 모듈을 가져오도록 변경 ★★★

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')