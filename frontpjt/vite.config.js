// frontpjt/vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path' // ★ path 모듈 import 추가

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    fs: {
      allow: [
        // 현재 vite.config.js 파일의 위치(frontpjt)를 기준으로 상위 디렉토리(financial_playground)를 허용
        path.resolve(__dirname, '..'), 
      ]
    }
  }
})