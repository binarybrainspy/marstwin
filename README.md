# MarsTwin — NASA Space Apps 2026

Solo build: **hardware-test first** (thermal cycling + mobility), **six dimensions**, coarse → validate → exclude famous → analogy cards with gap report.

## Quick start

```bash
# Science → JSON for the UI
pip install -r science/requirements.txt
python science/scripts/run_pipeline.py

# App
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173

## Six dimensions

1. Slope / roughness  
2. Diurnal ΔT  
3. Precipitation  
4. Vegetation (NDVI)  
5. Mineralogy  
6. Ice / permafrost  

## Layout

| Path | Role |
|------|------|
| `apps/web` | React + Vite UI |
| `science/` | Scoring pipeline → `apps/web/public/data/` |
| `docs/` | Architecture & playbook |

## Demo path

Home → Screen (fingerprint) → Validate (exclude famous) → Analogy card (transfers / breaks / tests / gaps)
