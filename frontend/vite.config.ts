/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// En développement, Vite relaie /api vers le backend, comme Nginx le fait en
// conteneur : l'interface et l'API partagent une seule adresse (US-001).
const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { '/api': backendUrl },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/shared/config/test-setup.ts',
  },
})
