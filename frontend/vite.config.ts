import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api/users': {
        target: 'http://user-service:8000',
        changeOrigin: true,
        rewrite: (path) => {
          // Auth endpoints are at root level: /auth/login, /auth/me
          if (path.indexOf('/api/users/auth/') === 0) {
            return path.replace(/^\/api\/users/, '');
          }
          // User CRUD endpoints are under /users: /users, /users/{id}
          return path.replace(/^\/api\/users/, '/users');
        },
      },
      '/api/flights': {
        target: 'http://flight-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/flights/, '/flights'),
      },
      '/api/hotels': {
        target: 'http://hotel-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/hotels/, '/hotels'),
      },
      '/api/cars': {
        target: 'http://car-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/cars/, '/cars'),
      },
      '/api/admin': {
        target: 'http://admin-service:8000',
        changeOrigin: true,
        secure: false,
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            // Ensure Authorization header is forwarded
            if (req.headers.authorization) {
              proxyReq.setHeader('Authorization', req.headers.authorization);
            }
          });
        },
        rewrite: (path) => path.replace(/^\/api\/admin/, ''),
      },
      '/api/search': {
        target: 'http://search-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/search/, '/search'),
      },
      '/api/booking': {
        target: 'http://booking-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/booking/, ''),
      },
      '/api/billing': {
        target: 'http://billing-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/billing/, ''),
      },
      '/api/ai': {
        target: 'http://ai-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ai/, '/api'),
      },
      '/api/deals': {
        target: 'http://ai-service:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/deals/, '/api/deals'),
      },
    },
  },
})
