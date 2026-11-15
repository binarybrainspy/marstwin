# Data source roadmap (solo, hardware-test first)

Temperature rule: **air↔air** (POWER T2M vs MEDA) or **ground↔ground** (MODIS LST vs rover TIRS / Diviner). Never mix unlabeled.

Slope rule: **20 m baseline everywhere** (Earth DEM, USGS Jezero 20 m, LOLA). Null until computed.

Mineralogy: **null / weight 0** until citable (lunar especially).

---

## Earth (wire order)

| Priority | Source | Fills | Status |
|----------|--------|-------|--------|
| 1 | **NASA POWER** | `diurnal_temp_range` (T2M air), `precipitation` | **Live** (`science/lib/power.py`) |
| 2 | **DEM → 20 m slope** | `slope_roughness` | Scaffold (`compute_slopes_20m.py`) |
| 3 | **MODIS NDVI** (or GIBS NDVI) | `vegetation_ndvi` | Next |
| 4 | **MODIS LST** | optional ground ΔT track (parallel, labeled) | Later |
| 5 | **GIBS** | imagery basemap / NDVI tiles in UI | Later |
| 6 | **EMIT** | `mineralogy` for arid Earth AOIs | Later |

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
# Enrich + score (calls POWER, uses cache under science/cache/)
python science/scripts/run_pipeline.py

# Offline re-score from cache
python science/scripts/run_pipeline.py --skip-power

# Slope scaffold (DEMs local)
python science/scripts/compute_slopes_20m.py
```
