# MarsTwin — Architecture (Prep Only)

> **Status note:** This is the original design and scoping document. The app and pipeline are now implemented; see the root [`README.md`](../README.md) for the current system, setup and data contract. Product thesis, route map and scoring logic below still describe the shipped architecture.

**Working name:** MarsTwin (folder: `marstwin`)  
**Challenge:** Analog Earth Locations — characterize terrestrial analogs for Moon/Mars  
**Differentiation (default):** Method + case study, with **hardware-test use case** as the narrative spine (Option B), optionally scoped geographically (Africa arid/thermal sites) if data access favors it.

---

## 1. What we are building (product thesis)

Judges do **not** want another coarse global “looks like Mars” heatmap.

MarsTwin is a **decision tool**:

1. Pick a concrete **mission use case** (instrument test / ops rehearsal / resource prospecting / risk reduction).
2. Screen Earth coarsely on a small set of physical dimensions.
3. Refine top cells at finer resolution.
4. Show a **similarity fingerprint** (per-dimension), not one score.
5. Validate that known analogs rank high → exclude them → surface **new** candidates.
6. Deliver an **Analogy Card + Gap Report** (what transfers / what breaks / what to test).

The React app is the **story + interaction layer**. The science lives in a thin data layer (JSON products from a notebook/script pipeline).

---

## 2. Split of responsibilities (critical for 48h)

| Layer | Tech | Owns | Does NOT own |
|-------|------|------|--------------|
| **Science pipeline** | Python (notebooks / scripts) + NASA APIs / GeoTIFF / CSV | Feature rasters, coarse screen, validation, fine refine, export JSON | Pretty UI |
| **App** | React + Vite + TypeScript | Map, fingerprints, analogy cards, gap report, use-case selector, demo flow | Heavy geospatial compute |
| **Static products** | `public/data/*.json` (+ optional small GeoJSON) | Demo-ready snapshots so UI never blocks on Earthdata | Live planetary processing |

**Speed rule:** On Day 1, get *one* end-to-end path working with **fixture JSON** first. Swap in real scores as the pipeline finishes. Never couple UI progress to API uptime.

---

## 3. System diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USE CASE PROFILE                         │
│  e.g. "rover wheel + thermal cycling rehearsal"              │
│  → weights which dimensions matter                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │   TARGET PROFILES (Moon / Mars)    │
         │   cited scalars + ranges            │
         └─────────────────┬─────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │           COARSE SCREEN (Earth grid)         │
    │  slope, roughness T, precip, NDVI, ice, …        │
    │  → ranked cells + per-dim distances          │
    └──────────────────────┬──────────────────────┘
                           │
              ┌────────────▼────────────┐
              │ VALIDATION GATE         │
              │ known analogs rank high │
              │ then EXCLUDE famous set │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │ FINE REFINE (AOIs)      │
              │ higher-res DEM/LST/etc  │
              └────────────┬────────────┘
                           │
         ┌─────────────────▼─────────────────┐
         │     ANALOGY CARD + GAP REPORT      │
         │  transfers / breaks / test plan    │
         └─────────────────┬─────────────────┘
                           │
                    JSON export
                           │
         ┌─────────────────▼─────────────────┐
         │     React + Vite presentation      │
         │  Map · Fingerprint · Cards · Demo  │
         └───────────────────────────────────┘
```

---

## 4. Recommended tech stack (Day-1 install list)

### Frontend
- **Vite + React + TypeScript**
- **React Router** — 4–5 routes max
- **Map:** `maplibre-gl` + `react-map-gl` (or Leaflet if MapLibre fights you — pick one and stick)
- **Charts:** `recharts` for radar/fingerprint bars
- **Styling:** plain CSS modules or one utility (avoid design-system rabbit holes)
- **State:** React state + URL params; no Redux

### Science (separate folder, not in Vite bundle until exported)
- Python 3.11+
- `numpy`, `pandas`, `xarray`, `rasterio` / `rioxarray` (as needed)
- `requests` + Earthdata auth for POWER / GIBS / etc.
- Jupyter only if it helps *you* iterate faster

### Hosting for demo
- Static Vite build (GitHub Pages / Netlify / local) + committed `public/data/`

---

## 5. Repository layout (create on Day 1, not before)

```
marstwin/
  apps/
    web/                 # Vite React app
      src/
        app/             # routes, layout
        features/
          usecase/       # use-case selector + weights
          map/           # coarse results + AOI refine view
          fingerprint/   # per-dimension similarity
          analogy/       # analogy card + gap report
          validation/    # known-analog check UI
        shared/          # types, ui primitives, formatters
      public/
        data/            # frozen JSON products for demo
  science/
    notebooks/
    scripts/
    profiles/            # moon/mars target YAML or JSON
    validation/
  docs/                  # this prep pack (allowed before event)
```

Until terms are confirmed, keep only `docs/` (and strategy markdown) in the repo.

---

## 6. Core domain objects

See `DATA_CONTRACTS.md` for full schemas. Mental model:

- **UseCase** — mission intent + dimension weights + “Earth limits” checklist
- **TargetProfile** — Moon or Mars site fingerprint (cited)
- **EarthCell** — coarse grid cell with feature vector
- **SimilarityResult** — per-dimension scores + composite (composite is secondary UI)
- **KnownAnalog** — validation set (Atacama, Dry Valleys, Iceland, Hawaii, …)
- **CandidateSite** — post-exclusion AOI with fine metrics
- **AnalogyCard** — transfers / breaks / tests / scale notes
- **GapReport** — gravity, vacuum, radiation, atmosphere, biosphere, logistics

---

## 7. UI information architecture (minimal)

| Route | Purpose | Judge signal |
|-------|---------|--------------|
| `/` | Hook: use case → method in 30s | Clarity |
| `/screen` | Coarse map + fingerprint for hovered/selected cell | Scale awareness |
| `/validate` | Known analogs rank high; toggle “exclude famous” | Scientific honesty |
| `/candidates/:id` | Analogy card + gap report + what to test | Characterization |
| `/method` | Short methods page (features, sources, limits) | Credibility |

**First viewport of `/`:** product name, one sentence thesis, one CTA (“Start from a use case”). No dashboard clutter.

---

## 8. Scoring method (product logic, not code)

### Dimensions (v1 — keep ≤ 8)
1. Slope / roughness  
2. Diurnal temperature range  
3. Precipitation / aridity  
4. Vegetation (NDVI)  
5. Surface mineralogy proxy (where available; else “unknown”)  
6. Ice / permafrost indicator  
7. *(optional)* Dust / albedo proxy  
8. *(optional)* Accessibility / logistics (Earth-only, for test planning — label as non-planetary)

### Similarity
- Per dimension: normalized distance → similarity in `[0, 1]`
- Missing data: mark `null`, **do not** invent; show “unknown” on fingerprint
- Composite: weighted mean using **UseCase weights** (this is the differentiation hook)

### Validation protocol
1. Run coarse screen with fixed Moon + Mars targets  
2. Assert known analogs appear in top-N (document N, e.g. 5% of land cells)  
3. Exclude known set  
4. Rank remaining → pick 1–2 for fine refine + analogy cards  

### Gap report (always on screen for a candidate)
Hard Earth limits that never “score away”:
- Gravity ≠ Moon/Mars  
- Atmosphere / vacuum  
- Radiation environment  
- Magnetic field / plasma  
- Biosphere contamination risk  
- Temporal / seasonal mismatch  

---

## 9. Differentiation choices (decide tonight)

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **A Africa-focus** | Geographic story, less “same Atacama again” | Need deeper than Tibesti/Ahaggar name-drop | Good *scope* for refine AOIs |
| **B Hardware-test first** | Clear use case; judges love specificity | Must stay concrete | **Primary narrative** |
| A+B | Best of both | Easy to over-scope | Do B globally coarse, refine 1 African + 1 other only if time |

**Default decision for speed:**  
Use case = *thermal cycling + mobility surface rehearsal for a lunar south-pole–adjacent ops concept* **or** *Mars arid dust/thermal instrument checkout*.  
Coarse screen global (or arid-land mask). Fine case study = **1 new site** done excellently.

---

## 10. Risk register

| Risk | Mitigation |
|------|------------|
| Earthdata / API friction | Fixture JSON path Day 1 morning |
| Over-building 3D globe | 2D MapLibre + fingerprint; skip Cesium |
| Famous-site rediscovery | Validation → exclude → new candidates UI is mandatory |
| Scope explosion | One Moon target + one Mars target; one use case; one deep card |
| Rules ambiguity | Read 2026 terms first thing; if code-before-event banned, only docs tonight |

---

## 11. What “done” looks like for submission

1. Working demo: use case → map → validate/exclude → analogy card  
2. Written methods + sources  
3. Gap report that names Earth limits explicitly  
4. Clear statement of scale (coarse cell size → refine resolution)  
5. Video walkthrough ≤ a few minutes  

Polish is secondary to a coherent science story.
