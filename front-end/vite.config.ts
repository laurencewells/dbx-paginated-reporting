import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: resolve(__dirname, '../back-end/static'),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          codemirror: [
            '@codemirror/commands',
            '@codemirror/lang-html',
            '@codemirror/state',
            '@codemirror/theme-one-dark',
            '@codemirror/view',
            'codemirror',
          ],
          chartjs: ['chart.js'],
          mustache: ['mustache'],
          dompurify: ['dompurify'],
        },
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
})
