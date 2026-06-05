import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: '/static/vue/',
  build: {
    outDir: '../../lossSimulator/static/vue',
    emptyOutDir: true,
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
