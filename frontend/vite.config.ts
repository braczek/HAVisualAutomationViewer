import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [basicSsl()],
  base: '/local/visualautoview/',
  build: {
    outDir: 'dist',
    minify: true,
    sourcemap: true,
    rollupOptions: {
      input: {
        main: 'index.html',
        panel: 'src/panel.ts' // Build panel as separate entry
      },
      output: {
        entryFileNames: (chunkInfo) => {
          // Panel should be named specifically for HA to find it
          if (chunkInfo.name === 'panel') {
            return 'visualautoview-panel.js';
          }
          return '[name]-[hash].js';
        }
      }
    }
  },
  server: {
    port: 3000,
    https: true,
    proxy: {
      '/api': {
        target: 'http://192.168.1.7:8123',
        changeOrigin: true
      }
    }
  }
});
