import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 17890,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://localhost:8998',
        changeOrigin: true,
      },
    },
  },
})
