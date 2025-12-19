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
        main: 'index.html'
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
