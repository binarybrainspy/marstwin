import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { setWorkerUrl } from 'maplibre-gl'
import './index.css'
import App from './App.tsx'

// Vite's dependency pre-bundling and dev transforms rewrite MapLibre's internal
// worker URL to a path it does not serve. Point it at the raw worker emitted by
// the Vite plugin instead.
setWorkerUrl(`${import.meta.env.BASE_URL}maplibre-gl-worker.mjs`)

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
