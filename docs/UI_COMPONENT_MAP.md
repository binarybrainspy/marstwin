# UI Component Map (React + Vite)

Build order for Day 1: **shell → fixtures → map → fingerprint → validation → analogy card**.

---

## Route → screen → components

### `/` — Landing / thesis
```
AppShell
  HeroBrand ("MarsTwin" or final name)
  OneLineThesis
  CtaGroup → /screen?usecase=...
  UseCasePicker (3 cards max, not a dashboard)
```
**Content budget:** brand, one headline, one sentence, CTAs. No stats strip.

### `/screen` — Coarse screen
```
AppShell
  UseCaseSummary (compact)
  TargetToggle (Moon | Mars)
  MapPanel
    CoarsePointsLayer | Heat-ish opacity by composite
    SelectionMarker
  SidePanel
    FingerprintChart (radar or grouped bars)
    DimensionLegend
    RankMeta (cell id, lat/lon, composite secondary)
  ActionBar → "Run validation" | "Open as candidate draft"
```

### `/validate`
```
AppShell
  ValidationTable (known analogs + rank)
  PassFailBanner
  ExcludeFamousToggle → recomputes candidate list from JSON field
  Link to top new candidates
```

### `/candidates/:id`
```
AppShell
  SiteHeader (name, coords, body targets)
  FingerprintChart (fine)
  AnalogySections
    TransfersList
    BreaksList
    TestsList
  GapReport
    GapItem (severity chips — keep quiet visually)
  ScaleNotes
  SourcesFooter
```

### `/method`
```
AppShell
  MethodBlocks (resolution, dims, sources, limits)
  CitationList
```

---

## Shared primitives (keep tiny)

| Component | Role |
|-----------|------|
| `AppShell` | Nav + main |
| `FingerprintChart` | Per-dim similarity; null → “unknown” |
| `GapList` | Hard limits always visible |
| `Cite` | Inline citation chip → source |
| `MapPanel` | MapLibre wrapper |

**Do not build:** 3D globe, auth, user accounts, realtime NASA streaming, design system library.

---

## State model (URL-first)

```
?usecase=uc_thermal_mobility
&target=moon_spole
&cell=c_12_34
&excludeFamous=1
```

Local React state only for hover and ephemeral UI. Selected entities should survive refresh via URL.

---

## Visual direction (decide once, implement fast)

Avoid default AI-landing tropes (purple gradients, cream+terracotta newspaper layouts).

Suggested direction for planetary analog tool:
- Dark-terrain or dust-neutral base with **one** accent (e.g. oxidized iron / basalt gray — pick hexes Day 1)
- Expressive display font for brand only; readable sans for body
- Map is the dominant visual on `/screen`
- Analogy card page is typographic + fingerprint, not card-grid spam

Write CSS variables in `:root` once:
```css
--bg, --surface, --text, --muted, --accent, --danger, --ok
```

---

## Demo script (record Day 2)

1. State the use case in one sentence.  
2. Show coarse map + fingerprint (not a single score).  
3. Show validation: known analogs rank high.  
4. Exclude famous sites → reveal new candidate.  
5. Open Analogy Card: transfers / breaks / tests.  
6. Explicitly read two hard Earth limits from Gap Report.  
7. Close with scale note (coarse ° → fine m).
