// frontpjt/src/main.js
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

// Bootstrap CSS 및 JS 가져오기
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import 'bootstrap-icons/font/bootstrap-icons.css'

/*
// Kakao SDK 초기화 로직 (main.js에서는 제거 또는 주석 처리)
if (window.Kakao && !window.Kakao.isInitialized()) {
  const KAKAO_JS_KEY = import.meta.env.VITE_KAKAO_MAP_JS_KEY;
  if (KAKAO_JS_KEY) {
    window.Kakao.init(KAKAO_JS_KEY);
    console.log('Kakao SDK initialized from main.js - THIS SHOULD BE REMOVED IF USED IN COMPONENT');
  } else {
    console.error('VITE_KAKAO_MAP_JS_KEY is not defined in .env file for main.js init.');
  }
} else if (!window.Kakao && import.meta.env.VITE_KAKAO_MAP_JS_KEY) {
  // 이 시점에는 window.Kakao가 없을 가능성이 매우 높습니다.
  console.error('Kakao SDK object (window.Kakao) not found in main.js. Ensure the SDK script in index.html is loaded and executed first.');
}
*/

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')