import { defineConfig } from 'vite';
import basicSsl from '@vitejs/plugin-basic-ssl';

export default defineConfig({
  plugins: [basicSsl()],
  build: {
    lib: {
      entry: 'src/index.ts',
      name: 'VisualAutoView',
      fileName: (format) => `visual-autoview.${format === 'es' ? 'js' : 'cjs'}`
    },
    minify: true,
    sourcemap: true,
    outDir: 'dist'
  },
  server: {
    port: 3000,
    https: true
  }
});
