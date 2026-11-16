# MarsTwin

**An analog Earth atlas for testing surface hardware against the Moon and Mars.**

MarsTwin screens twenty of Earth's driest, coldest and most barren landscapes against two concrete mission destinations — Jezero Crater on Mars and the lunar south-polar rim. It does not declare a site "Mars on Earth." It shows where the comparison holds, where it breaks, and what a field campaign must carry with it.

Built for **NASA Space Apps 2026 — Analog Earth Locations**.

---

## What the app does

| Route | What it answers |
|-------|-----------------|
| `/` | What is MarsTwin, and why does an analog atlas need a reality check? |
| `/screen` | Which Earth cells rank closest to Jezero or the lunar south pole, and why? |
| `/validate` | Do the famous analog sites survive the screen before new candidates are promoted? |
| `/candidates/:id` | What transfers, what breaks, what would we test, and what gaps remain? |
| `/method` | Which sources, weights, transforms, nulls and limitations produced the result? |

The atlas uses Esri World Imagery raster tiles for the interactive map, with a terrain layer and a place-label overlay. Every site also ships a static satellite thumbnail, so field cards and rankings remain useful even if the live map is unavailable.

### The demo path

1. **Overview** — the product thesis and the two destinations.
2. **Atlas** — choose Mars or the Moon, select a cell, inspect its six-signal fingerprint.
3. **Reality check** — confirm the known analogs pass, then remove them from the candidate pool.
4. **Field card** — read the transfers, the tests, the breaks and the gap report.
5. **Method** — audit the data run, sources, weights and deliberate blanks.

---

## The screen in one minute

MarsTwin compares six measurable signals. Each dimension has a named source, a target value and an explicit transform:

| Dimension | Earth source | Target source | Status |
|-----------|--------------|---------------|--------|
| Slope / roughness | DEM slope at a shared 20 m baseline | LOLA polar DEM + USGS Jezero 20 m | **Pending** — null until computed |
| Diurnal ΔT | NASA POWER T2M air climatology | MEDA air at Jezero; lunar ΔT null | **Live** — air↔air only |
| Precipitation | NASA POWER PRECTOTCORR | 0 for Mars / vacuum | **Live** |
| Vegetation (NDVI) | MODIS MOD13Q1 250 m, 2025 annual mean | 0 for a barren target | **Live** — 19/20 cells |
| Mineralogy | EMIT planned | Null until citable | **Blank** — weight 0 |
| Ice / permafrost | Coarse screening proxy | Lunar PSR relevance; low at Jezero | **Proxy** |

Similarity is calculated per dimension:

```text
similarity = 1 − clip(|earth − target| / scale, 0, 1)
```

The composite score is the weighted mean of the dimensions that have both values. If an observation is null, that dimension is excluded and the remaining weights are renormalised. **The composite is a screening aid. The six-signal fingerprint and the gap report are the real output.**

Current use-case weights:

| Signal | Weight |
|--------|--------|
| Diurnal ΔT | 32% |
| Slope / roughness | 28% |
| Precipitation | 18% |
| Vegetation (NDVI) | 14% |
| Ice / permafrost | 8% |
| Mineralogy | 0% |

### Validation rule

Known analogs are the control group. A destination passes when **at least one known analog lands in the top three of twenty**. Only after that gate does the pipeline remove the controls and promote new candidates.

Current result:

| Destination | Best control | Controls in top three | Status |
|-------------|--------------|-----------------------|--------|
| Mars — Jezero Crater | Atacama Desert, rank 1 | 1 | **Pass** |
| Moon — south-polar rim | McMurdo Dry Valleys, rank 1 | 2 | **Pass** |

Mars top five: Atacama (1), Western Desert Egypt (2), Taklamakan (3), Dasht-e Lut (4), Atacama valley floor (5).

Moon top five: McMurdo Dry Valleys (1), Atacama (2), Western Desert Egypt (3), Taklamakan (4), Tibesti (5).

The two promoted field cards are **Western Desert (Egypt)** and **Taklamakan**. They are new candidates because neither is in the known-analog control set.

---

## Data integrity rules

These are not stylistic choices. They are enforced in the pipeline and data contracts.

- **Slopes are null until computed at a shared 20 m baseline.** Coarser DEMs are flagged, never upsampled or quietly relabelled.
- **Temperature stays air↔air or ground↔ground.** Earth uses NASA POWER T2M air; Jezero uses MEDA air at 1.45 m. MODIS LST is a separate ground track and must be labelled before comparison.
- **Mineralogy is null and zero-weighted until a citable value exists.** No placeholder numbers.
- **NDVI is sourced or null.** MODIS MOD13Q1 is a 250 m point sample in a ~2 km box around the cell centre, not a 0.5° area mean. Missing coverage stays missing.
- **The Moon has no fabricated air ΔT.** Polar thermal behaviour is illumination-driven. The ~40 K PSR cold-trap regime is a hard gap, not an Earth similarity score.
- **Null beats a fake number.** An unknown observation is shown as unknown and excluded from the weighted score.

---

## Current data snapshot

From `apps/web/public/data/manifest.json`:

| Field | Value |
|-------|-------|
| Pipeline version | `0.6.0` |
| Generated | 16 November 2026 (local display) |
| Earth cells | 20 |
| Destinations | 2 |
| Known analogs | 4 |
| Promoted candidates | 2 |
| MODIS NDVI | MOD13Q1, 2025, 19/20 cells |
| Slope baseline | 20 m, status `pending`, 0/20 computed |

The one NDVI gap is **McMurdo Dry Valleys** — MODIS returns no coverage for that cell. It remains unknown.

---

## Run it

### Prerequisites

- Python 3.11+
- Node.js 20.19+ (or 22.12+)
- npm

### 1. Science pipeline

From the repository root:

```bash
pip install -r science/requirements.txt
python science/scripts/run_pipeline.py
```

The pipeline:

1. Loads `science/profiles/`.
2. Asserts the target-profile contracts.
3. Syncs profiles into `apps/web/public/data/`.
4. Enriches Earth cells with NASA POWER air climatology and MODIS NDVI.
5. Scores every cell against both destinations.
6. Runs the known-analog validation gate.
7. Builds candidate cards and the manifest.
8. Writes the static JSON products consumed by the frontend.

Useful flags:

```bash
# Offline re-score from cache (also skips NDVI fetches)
python science/scripts/run_pipeline.py --skip-power

# Refetch an external source even when a cache exists
python science/scripts/run_pipeline.py --force-power
python science/scripts/run_pipeline.py --force-ndvi

# Change the MODIS sample year
python science/scripts/run_pipeline.py --ndvi-year 2025
```

Caches live under `science/cache/` and are intentionally git-ignored.

### 2. Optional real 20 m slopes

The slope script needs local DEM rasters (`rasterio` is installed with the science requirements):

```bash
python science/scripts/compute_slopes_20m.py \
  --earth-dem dems/srtm_atacama.tif --aoi cell_atacama \
  --jezero-dem dems/jezero_20m.tif \
  --lola-dem dems/lola_spole.tif

# Write computed values into the profiles, then re-score
python science/scripts/compute_slopes_20m.py --jezero-dem dems/jezero_20m.tif --apply
python science/scripts/run_pipeline.py --skip-power
```

Slope statistics land in `science/cache/slopes_20m.json`. Hand-typed slopes are rejected by the contract check.

### 3. Imagery (optional, already committed)

```bash
# Earth satellite thumbnails + world locator from Esri World Imagery
python science/scripts/fetch_site_imagery.py

# Mars, Moon and analog reference imagery from the NASA Image Library
python science/scripts/fetch_nasa_imagery.py
```

Both scripts are idempotent. Add `--force` to refetch. Outputs go to `apps/web/public/images/`, with attribution in `sources.json` and `credits.json`.

### 4. Web app

```bash
cd apps/web
npm install
npm run dev
```

Open the local URL printed by Vite (default `http://localhost:5173`).

Production build:

```bash
cd apps/web
npm run build
npm run preview
```

The frontend reads only static files from `apps/web/public/data/` and `apps/web/public/images/`. There is no live backend or API dependency at demo time.

---

## Repository layout

```text
marstwin/
  apps/web/                 React + Vite + TypeScript frontend
    public/data/            Generated JSON products (committed)
    public/images/          Satellite + NASA reference imagery (committed)
    src/app/                Shell, routing, data provider
    src/features/           Map, fingerprint, candidate card, validation, method
    src/shared/             Types, data loading, formatting
  science/
    profiles/               Earth cells, targets, use cases, known analogs
    lib/                    POWER, NDVI, scoring, contracts, manifest
    scripts/                Pipeline, slope computation, imagery fetchers
    cache/                  Local API cache (git-ignored)
  docs/                     Contracts, sources, architecture, playbook
  REPORT_README.md          Report and slide-deck source material
```

---

## JSON products

| File | Purpose |
|------|---------|
| `manifest.json` | Data-run provenance: version, timestamp, counts, NDVI vintage, slope status, validation, sources, imagery paths |
| `usecases.json` | Mission intent and dimension weights |
| `targets.json` | Cited Moon/Mars target profiles |
| `known_analogs.json` | Control group used by the validation gate |
| `coarse_results.json` | Every cell × destination score and rank |
| `candidates.json` | Promoted field cards with transfers, tests, breaks and gaps |
| `method.json` | Human-readable method, transforms, exclusions and limitations |

The manifest is the frontend's source of truth for "what am I looking at?" It is surfaced in the top-bar data chip and footer, and expanded on the Method page.

---

## Known limitations

- **Slopes are not yet scored.** The 20 m baseline is locked, but the DEM products still need to be run locally. This is the largest open gap.
- **Mineralogy is excluded.** No citable per-site value is locked, so the dimension is null and weighted at zero.
- **Ice is a coarse proxy.** It is useful for screening, not for a claim that Earth ice equals PSR ice.
- **NDVI is a point sample.** A 250 m MODIS sample in a ~2 km box can differ from the bare fraction of the full 0.5° cell.
- **Earth cannot rehearse gravity, vacuum, radiation or planetary protection.** Those are reported as hard limits, never scored away.
- **The composite is not a site-selection verdict.** It is a shortlist generator.

---

## Documentation index

- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) — source roadmap, live/pending status, imagery and manifest commands
- [`science/README.md`](science/README.md) — pipeline internals, locked rules, outputs
- [`docs/DATA_CONTRACTS.md`](docs/DATA_CONTRACTS.md) — JSON shapes consumed by the frontend
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design and product logic
- [`REPORT_README.md`](REPORT_README.md) — narrative material for the written report and slide deck

---

## Credits

Earth imagery: **Esri, Maxar, Earthstar Geographics** (World Imagery and reference layers).  
Mars, Moon and analog reference imagery: **NASA / JPL-Caltech and partners**, via the NASA Image and Video Library.

Science and data sources: **NASA POWER**, **NASA ORNL DAAC MODIS MOD13Q1**, **NASA Perseverance MEDA**, **USGS Astrogeology**, **NASA LRO LOLA / Diviner**.

MarsTwin is a screening and communication tool, not a mission site-selection authority.
