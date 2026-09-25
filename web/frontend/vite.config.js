import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync, writeFileSync } from 'node:fs'
import { resolve } from 'node:path'

// Precache lazy-loaded editor/PDF chunks too: first offline navigation must
// not depend on whether a user happened to open that screen while online.
function offlineBuildManifest() {
  let outDir;
  return {
    name: 'diyargezen-offline-manifest',
    configResolved(config) { outDir = resolve(config.root, config.build.outDir); },
    writeBundle(_options, bundle) {
      const files = Object.keys(bundle).filter(name => /\.(js|css)$/.test(name)).map(name => '/' + name);
      const path = resolve(outDir, 'sw.js');
      const source = readFileSync(path, 'utf8');
      writeFileSync(path, source.replace('const BUILD_ASSETS = [];', 'const BUILD_ASSETS = ' + JSON.stringify(files) + ';')
        .replace('diyargezen-cache-v5', 'diyargezen-cache-' + Object.keys(bundle).find(name => /^assets\/index-.*\.js$/.test(name))));
    },
  };
}

// https://vitejs.dev/config/
export default defineConfig({
  base: './',
  plugins: [react(), offlineBuildManifest()],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'axios', 'lucide-react'],
          pdf: ['pdf-lib'],
        }
      }
    }
  },
  server: {
    host: '127.0.0.1',
    port: 5173,
    hmr: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
})

