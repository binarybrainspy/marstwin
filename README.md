# MarsTwin — NASA Space Apps 2026

Duo build: **hardware-test first** (thermal cycling + mobility), **six dimensions**, coarse → validate → exclude famous → analogy cards with gap report.

## Quick start

```bash
# Science → JSON for the UI (calls NASA POWER; caches under science/cache/)
python science/scripts/run_pipeline.py

# App
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173

## Locked science rules

- **Slopes:** null until computed at a shared 20 m baseline (Earth DEM + LOLA + USGS Jezero); coarser DEMs are flagged, not relabeled
- **Thermal:** air↔air (POWER T2M vs MEDA ~60 K at Jezero); Moon PSR ~40 K is a **gap**, not a score
- **Mineralogy:** null / weight 0 until citable
- **Vegetation:** MODIS MOD13Q1 250 m annual mean (2025) in a ~2 km point sample; no coverage or fetch failure → null, never a stub
- **Hardware-test narrative:** thermal cycling + mobility

Sources roadmap: `docs/DATA_SOURCES.md`

## Six dimensions

1. Slope / roughness  
2. Diurnal ΔT (air)  
3. Precipitation  
4. Vegetation (NDVI)  
5. Mineralogy (zero-weighted for now)  
6. Ice / permafrost  

## Demo path

Home → Screen (fingerprint) → Validate (exclude famous) → Analogy card (transfers / breaks / tests / gaps)
