import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Configuracion minima para Vite con React.
// El puerto se fija para que coincida con el publicado por docker-compose.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
})
