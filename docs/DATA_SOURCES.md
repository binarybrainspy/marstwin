# Data source roadmap (solo, hardware-test first)

Temperature rule: **air↔air** (POWER T2M vs MEDA) or **ground↔ground** (MODIS LST vs rover TIRS / Diviner). Never mix unlabeled.

Slope rule: **20 m baseline everywhere** (Earth DEM, USGS Jezero 20 m, LOLA). Null until computed; DEMs coarser than 20 m are flagged, never upsampled or relabeled.

Mineralogy: **null / weight 0** until citable (lunar especially).

---

## Earth (wire order)

| Priority | Source | Fills | Status |
|----------|--------|-------|--------|
| 1 | **NASA POWER** | `diurnal_temp_range` (T2M air), `precipitation` | **Live** (`science/lib/power.py`) |
| 2 | **DEM → 20 m slope** | `slope_roughness` | **Script ready** — needs local DEMs (`compute_slopes_20m.py`) |
| 3 | **MODIS NDVI** (MOD13Q1 250 m, ORNL DAAC) | `vegetation_ndvi` | **Live** (`science/lib/ndvi.py`) — 2025 annual mean; null if no coverage |
| 4 | **MODIS LST** | optional ground ΔT track (parallel, labeled) | Later |
| 5 | **GIBS** | imagery basemap / NDVI tiles in UI | Later |
| 6 | **EMIT** | `mineralogy` for arid Earth AOIs | Later |

NDVI sampling: MOD13Q1 16-day composites, annual mean in a ±1 km box (~2 km across) around the cell centre — a **point sample, not a 0.5° area mean**. The ORNL subset API serves at most 10 composites per request, so a year is fetched in ~3 windows and cached in `science/cache/modis_ndvi.json`. Missing coverage (e.g. McMurdo Dry Valleys) stays null; it is never back-filled with a guess.

## Mars

| Source | Use |
|--------|-----|
| **MEDA** (Perseverance) | Jezero air diurnal ~60 K — **in targets.json** |
| **USGS Jezero 20 m DEM** | slope at 20 m baseline |
| **MOLA** | regional context / fallback topography |
| **HiRISE** | fine morphologic storytelling (not coarse score) |
| **Odyssey neutrons** | ice proxy when use case needs it |
| **CRISM** | mineralogy when cited |

## Moon

| Source | Use |
|--------|-----|
| **LRO LOLA** | polar DEM → 20 m slopes |
| **Diviner** | PSR cold traps (~40 K) as **gap**, not fake Earth match; surface T when comparing to LST |
| **LROC** | imagery / context |

---

## Commands

```bash
# Enrich + score (POWER + MODIS NDVI, cached under science/cache/)
python science/scripts/run_pipeline.py

# Offline re-score from cache (--skip-power also disables NDVI fetches)
python science/scripts/run_pipeline.py --skip-power

# NDVI controls
python science/scripts/run_pipeline.py --ndvi-year 2025   # sample year
python science/scripts/run_pipeline.py --force-ndvi      # refetch MOD13Q1
python science/scripts/run_pipeline.py --skip-ndvi       # cached NDVI only

# Slopes at the shared 20 m baseline (Horn 3x3; needs rasterio + local DEMs)
python science/scripts/compute_slopes_20m.py \
  --earth-dem dems/srtm_atacama.tif --aoi cell_atacama \
  --jezero-dem dems/jezero_20m.tif \
  --lola-dem dems/lola_spole.tif

# Write computed means into targets.json + earth_cells.csv, then re-score
python science/scripts/compute_slopes_20m.py --jezero-dem dems/jezero_20m.tif --apply
python science/scripts/run_pipeline.py --skip-power
```

Stats land in `science/cache/slopes_20m.json` (mean, median, P95, max, % >10/15/20/25°, baseline status).
