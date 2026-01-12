import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    allowedHosts: ['localhost', '.ngrok-free.app'],
  },
  build: { target: 'esnext', emptyOutDir: true, },
  publicDir: './public',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  }
});
