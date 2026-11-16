# Data sources and provenance

MarsTwin follows three locked rules:

- **Temperature:** air↔air (NASA POWER T2M vs MEDA) or ground↔ground (MODIS LST vs rover TIRS / Diviner). Never mix unlabeled.
- **Slope:** a shared **20 m baseline** everywhere (Earth DEM, USGS Jezero 20 m, LOLA). Null until computed; coarser DEMs are flagged, never upsampled or relabelled.
- **Mineralogy:** **null / weight 0** until citable.

A fourth rule governs the frontend: **null beats a fake number**. Missing or failed observations stay visible as unknown and are excluded from the weighted score.

---

## Earth sources

| Priority | Source | Fills | Status |
|----------|--------|-------|--------|
| 1 | **NASA POWER** | `diurnal_temp_range` (T2M air), `precipitation` | **Live** — `science/lib/power.py` |
| 2 | **DEM → 20 m slope** | `slope_roughness` | **Script ready** — needs local DEMs (`compute_slopes_20m.py`) |
| 3 | **MODIS NDVI** (MOD13Q1 250 m, ORNL DAAC) | `vegetation_ndvi` | **Live** — 2025 annual mean, 19/20 cells |
| 4 | **MODIS LST** | optional ground-temperature track (parallel, labelled) | Later |
| 5 | **Esri World Imagery** | interactive basemap + static site thumbnails | **Live** — UI only, not scored |
| 6 | **EMIT** | `mineralogy` for arid Earth AOIs | Later |

### NDVI sampling

MODIS MOD13Q1 16-day composites, annual mean in a ±1 km box (~2 km across) around the cell centre — a **point sample, not a 0.5° area mean**. The ORNL subset API serves at most 10 composites per request, so a year is fetched in ~3 windows and cached in `science/cache/modis_ndvi.json`.

Missing coverage (currently McMurdo Dry Valleys) stays null. It is never back-filled with a guess.

---

## Mars sources

| Source | Use | Status |
|--------|-----|--------|
| **MEDA** (Perseverance) | Jezero air diurnal amplitude ~60 K at 1.45 m | **In `targets.json`** |
| **USGS Jezero 20 m DEM** | slope at the shared 20 m baseline | Pending local DEM |
| **MOLA** | regional context / fallback topography | Context only |
| **HiRISE** | fine morphologic storytelling | Not in the score |
| **Odyssey neutrons** | ice proxy when the use case needs it | Later |
| **CRISM** | mineralogy when cited | Later; currently null |

---

## Moon sources

| Source | Use | Status |
|--------|-----|--------|
| **LRO LOLA** | polar DEM → 20 m slopes | Pending local DEM |
| **Diviner** | PSR cold traps (~40 K) as a **hard gap**, not an Earth match; surface temperature when comparing to LST | Context / gap |
| **LROC** | imagery and context | Context only |

The lunar target's diurnal air ΔT is deliberately null. Polar thermal behaviour is illumination-driven, and no Earth surface reaches the ~40 K cold-trap regime.

---

## Frontend imagery

The app ships with static imagery so the demo does not depend on live tile availability:

```bash
# Earth site thumbnails + world locator (Esri World Imagery)
python science/scripts/fetch_site_imagery.py

# Mars, Moon and analog reference imagery (NASA Image and Video Library)
python science/scripts/fetch_nasa_imagery.py
```

Both scripts are idempotent; add `--force` to refetch. Outputs:

| Path | Contents |
|------|----------|
| `apps/web/public/images/sites/{cellId}.jpg` | 20 satellite thumbnails, 640×400 |
| `apps/web/public/images/world.jpg` | world locator fallback |
| `apps/web/public/images/sources.json` | Esri attribution and site bounding boxes |
| `apps/web/public/images/target-mars.jpg` | Jezero Crater reference |
| `apps/web/public/images/target-moon.jpg` | lunar south-pole reference |
| `apps/web/public/images/analog-*.jpg` | Atacama and Dry Valleys references |
| `apps/web/public/images/hero-mars.jpg` | Mars hero image |
| `apps/web/public/images/credits.json` | NASA asset IDs, titles and credits |

The interactive map uses these Esri raster endpoints directly:

```text
Imagery:  https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}
Relief:   https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}
Labels:   https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}
```

Attribution is shown in the MapLibre control, in the app footer and in `sources.json`.

---

## Data manifest

Every pipeline run writes `apps/web/public/data/manifest.json` (pipeline `0.6.0`, schema `1`). It records:

- `generatedAt` and `pipelineVersion`;
- cell, target, known-analog and candidate counts;
- NDVI product, band, year, box size, cells with data and cells missing;
- slope baseline, method, status and computed cells;
- validation pass/fail with best known-analog rank;
- source list and URLs;
- imagery paths and credit text;
- the list of frontend JSON files.

The frontend reads the manifest through `DataProvider` and surfaces the run date and data status in the top bar, footer and Method page. The manifest is the answer to "which data produced this screen?"

---

## Commands

```bash
# Enrich + score (POWER + MODIS NDVI, cached under science/cache/)
python science/scripts/run_pipeline.py

# Offline re-score from cache (--skip-power also disables NDVI fetches)
python science/scripts/run_pipeline.py --skip-power

# NDVI controls
python science/scripts/run_pipeline.py --ndvi-year 2025   # sample year
python science/scripts/run_pipeline.py --force-ndvi       # refetch MOD13Q1
python science/scripts/run_pipeline.py --skip-ndvi        # cached NDVI only

# Slopes at the shared 20 m baseline (Horn 3x3; needs rasterio + local DEMs)
python science/scripts/compute_slopes_20m.py \
  --earth-dem dems/srtm_atacama.tif --aoi cell_atacama \
  --jezero-dem dems/jezero_20m.tif \
  --lola-dem dems/lola_spole.tif

# Write computed means into targets.json + earth_cells.csv, then re-score
python science/scripts/compute_slopes_20m.py --jezero-dem dems/jezero_20m.tif --apply
python science/scripts/run_pipeline.py --skip-power
```

Slope statistics land in `science/cache/slopes_20m.json` (mean, median, P95, max, % >10/15/20/25°, baseline status).

---

## Attribution

- Earth imagery: **Esri, Maxar, Earthstar Geographics**.
- Mars / Moon / analog imagery: **NASA / JPL-Caltech and partners**, via the NASA Image and Video Library.
- Science data: **NASA POWER**, **NASA ORNL DAAC MODIS MOD13Q1**, **NASA Perseverance MEDA**, **USGS Astrogeology**, **NASA LRO LOLA / Diviner**.

See [`../README.md`](../README.md) for setup and [`../REPORT_README.md`](../REPORT_README.md) for report and slide material.
