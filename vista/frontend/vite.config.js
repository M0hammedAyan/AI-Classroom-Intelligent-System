import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

import { reticle } from '@reticlehq/vite-plugin';
export default defineConfig({
  plugins: [reticle({ port: 4460 }), react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://127.0.0.1:8002',
        ws: true,
      },
    },
  },
});
