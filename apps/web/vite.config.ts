import { createReadStream, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

const maplibreWorkerPath = fileURLToPath(
  new URL(
    './node_modules/maplibre-gl/dist/maplibre-gl-worker.mjs',
    import.meta.url,
  ),
)

// Vite transforms MapLibre's already-bundled worker and injects module imports,
// which leaves the worker request pending. Serve and emit the package file raw
// so dev and production use the same self-contained worker.
function maplibreWorker(): Plugin {
  return {
    name: 'maplibre-worker',
    configureServer(server) {
      server.middlewares.use('/maplibre-gl-worker.mjs', (_req, res) => {
        res.setHeader('Content-Type', 'text/javascript; charset=utf-8')
        res.setHeader('Cache-Control', 'no-cache')
        createReadStream(maplibreWorkerPath).pipe(res)
      })
    },
    generateBundle() {
      this.emitFile({
        type: 'asset',
        fileName: 'maplibre-gl-worker.mjs',
        source: readFileSync(maplibreWorkerPath),
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), maplibreWorker()],
  // Pre-bundling maplibre-gl rewrites its internal worker URL to a path Vite
  // does not serve in dev. Serving the package directly keeps the main module
  // and the worker on the same resolved instance.
  optimizeDeps: {
    exclude: ['maplibre-gl'],
  },
})
