import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000, // Or any port you prefer
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Assuming backend runs on 8000
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'ws://localhost:8000', // Proxy WebSocket connections
        ws: true,
        changeOrigin: true,
      }
    }
  }
})
