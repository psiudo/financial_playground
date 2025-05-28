// frontpjt/vite.config.js
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: { // ★★★ server 객체 확인 ★★★
    proxy: { // ★★★ 이 부분이 정확히 있는지 확인 ★★★
      '/api': { 
        target: 'http://localhost:8000', // 실제 Django 백엔드 서버 주소
        changeOrigin: true,
      }
    },
    fs: {
      allow: [
        path.resolve(__dirname, '..'),
      ]
    }
  }
})