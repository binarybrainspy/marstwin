# 48-Hour Playbook (Nov 14–15)

Assumption: participant terms allow creating all code during the event. Re-check before first `npm create`.

---

## Hour 0–1 — Bootstrap (copy-paste)

### 1. Confirm terms, then scaffold

```bash
# from marstwin/
npm create vite@latest apps/web -- --template react-ts
cd apps/web
npm install
npm install react-router-dom maplibre-gl react-map-gl recharts
npm run dev
```

If MapLibre/react-map-gl version conflict wastes >30 min → fall back to `leaflet` + `react-leaflet`.

### 2. Folder stubs inside `apps/web/src`

```
app/
features/usecase/
features/map/
features/fingerprint/
features/analogy/
features/validation/
shared/types.ts          # paste from DATA_CONTRACTS.md
public/data/             # empty JSON fixtures first
```

### 3. Science side

```bash
mkdir -p science/profiles science/scripts science/validation
```

Put filled target profiles into `science/profiles/*.json`.

### 4. Fixture-first rule

Before any Earthdata call, create minimal:
- `usecases.json`
- `targets.json`
- `known_analogs.json`
- `coarse_results.json` (20–50 fake cells + 4 known-analog cells)
- `candidates.json` (1–2 stubs)
- `method.json`

Wire UI end-to-end on fixtures. Then replace numbers with pipeline output.

---

## Day 1 schedule

| Block | Focus | Exit criteria |
|-------|-------|---------------|
| H0–1 | Scaffold + routes + fixtures | App navigates all 5 routes |
| H1–4 | Fingerprint + map on fixtures | Select cell → see per-dim scores |
| H4–8 | Pipeline: pull 2–3 Earth layers, coarse grid | Real `coarse_results.json` for a region or global coarse |
| H8–11 | Validation + exclude famous | Table shows known analogs high; toggle works |
| H11–14 | Pick top new candidates; start fine metrics | 1 site with real-ish fine numbers |
| Buffer | Sleep / food | Do not start Cesium |

**Day 1 “must green”:** fixture UI + real coarse file + validation narrative.

---

## Day 2 schedule

| Block | Focus | Exit criteria |
|-------|-------|---------------|
| Morning | Analogy card + gap report for top site | Transfers / breaks / tests filled |
| Mid | Method page + citations | Sources listed |
| Afternoon | Polish map, fix demo path | 3-minute click path rehearsed |
| Late | Record demo + write submission text | Video + project page draft |
| Final | Freeze `public/data`, build static | `npm run build` works offline |

---

## Parallelization (if team of 2–3)

| Person | Day 1 | Day 2 |
|--------|-------|-------|
| A Science | Profiles, rasters, scoring | Fine refine, citations |
| B Frontend | Routes, map, fingerprint | Analogy card polish, demo |
| C Story | Use-case text, gap bullets | Video script, submission |

Solo: morning UI fixtures → afternoon one Earth region pipeline → evening validation story.

---

## Kill list (do not do)

- Full global beautiful 3D globe
- Live streaming all NASA APIs in the browser
- Perfect mineralogy globally
- More than **two** deep analogy cards
- Auth, accounts, databases
- Redesigning visual theme after Hour 3 Day 2

---

## Submission package checklist

- [ ] Live demo URL or clear local run instructions
- [ ] Short video following demo script in `UI_COMPONENT_MAP.md`
- [ ] Project summary answering: similar / how / breaks / tests
- [ ] Data sources + acknowledgments
- [ ] Explicit Earth-limits gap section
- [ ] Statement of scale (coarse → fine)

---

## Emergency paths

| Failure | Fallback |
|---------|----------|
| Earthdata blocked | Literature-derived regional stats + honest method limits |
| Global grid too slow | Screen one continent / arid mask only; say so |
| MapLibre broken | Static images + SVG fingerprint still beats nothing |
| No “new” site convincing | Deepen gap analysis + use-case specificity; judges reward honesty |
