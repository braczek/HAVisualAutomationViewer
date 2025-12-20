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
        panel: 'src/panel.ts'
      },
      output: {
        entryFileNames: 'visualautoview-panel.js'
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
