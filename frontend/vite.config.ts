import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'

const backendProxyTarget = process.env.BACKEND_URL || 'http://localhost:5000'
const gatewayProxyTarget = process.env.SSE_GATEWAY_URL || 'http://localhost:3001'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), TanStackRouterVite()],
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '@/components': resolve(__dirname, './src/components'),
      '@/lib': resolve(__dirname, './src/lib'),
      '@/types': resolve(__dirname, './src/types'),
      '@/hooks': resolve(__dirname, './src/hooks'),
      '@/routes': resolve(__dirname, './src/routes'),
      '@/api': resolve(__dirname, './src/lib/api'),
    },
  },
  server: {
    port: 3000,
    allowedHosts: true,
    host: true,
    open: true,
    proxy: {
      '/api/sse': {
        target: gatewayProxyTarget,
        changeOrigin: true,
        secure: false,
      },
      '/api': {
        target: backendProxyTarget,
        changeOrigin: true,
        secure: false,
      }
    },
    watch: process.env.VITE_TEST_MODE === 'true'
      ? {
          ignored: ['**']
        }
      : undefined
  },
})
