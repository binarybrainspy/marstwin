# Data Contracts

Frozen JSON shapes the Vite app will consume from `public/data/`.  
Implement types in TypeScript on Day 1 by copying these interfaces almost verbatim.

---

## Files the UI expects

```
public/data/
  usecases.json
  targets.json
  known_analogs.json
  coarse_results.json      # can be large — keep demo subset if needed
  candidates.json          # post-exclusion refined sites
  method.json              # human-readable methods blurb + sources
```

Optional later:
- `coarse_results.geojson` for map polygons/points
- `refine/<siteId>.json` for fine-resolution metrics

---

## TypeScript interfaces (copy on Day 1)

```ts
/** Mission intent that reweights similarity dimensions */
export type DimensionKey =
  | "slope_roughness"
  | "diurnal_temp_range"
  | "precipitation"
  | "vegetation_ndvi"
  | "mineralogy"
  | "ice_permafrost"
  | "albedo_dust"      // optional
  | "logistics";       // Earth-only planning factor; never claim planetary similarity

export interface UseCase {
  id: string;
  title: string;
  summary: string;
  body: "moon" | "mars" | "both";
  /** Weights must sum to ~1 for active dims; omit or 0 for unused */
  weights: Partial<Record<DimensionKey, number>>;
  earthLimitsAlways: string[]; // short bullets shown in gap UI
}

export interface CitedValue {
  value: number | null;
  unit: string;
  source: string;      // citation short form
  sourceUrl?: string;
  notes?: string;
}

export interface TargetProfile {
  id: string;
  body: "moon" | "mars";
  name: string;
  lat: number;
  lon: number;
  rationale: string;
  features: Partial<Record<DimensionKey, CitedValue>>;
}

export interface FeatureVector {
  values: Partial<Record<DimensionKey, number | null>>;
  units?: Partial<Record<DimensionKey, string>>;
}

export interface EarthCell {
  id: string;
  lat: number;
  lon: number;
  /** Coarse cell size in degrees, e.g. 0.5 */
  cellDeg: number;
  features: FeatureVector;
  regionHint?: string; // e.g. "Namib", "Sahara"
}

export interface DimensionScore {
  key: DimensionKey;
  similarity: number | null; // 0..1 or null if missing
  earthValue: number | null;
  targetValue: number | null;
  note?: string;
}

export interface SimilarityResult {
  cellId: string;
  targetId: string;
  useCaseId: string;
  dimensions: DimensionScore[];
  /** Secondary — never the only thing shown */
  composite: number | null;
  rank?: number;
}

export interface KnownAnalog {
  id: string;
  name: string;
  lat: number;
  lon: number;
  whyFamous: string;
  bodies: Array<"moon" | "mars">;
  /** Expected to appear in top fraction during validation */
  cellId?: string;
}

export interface GapItem {
  id: string;
  category:
    | "gravity"
    | "atmosphere_vacuum"
    | "radiation"
    | "magnetic"
    | "biosphere"
    | "scale"
    | "temporal"
    | "logistics"
    | "other";
  title: string;
  detail: string;
  severity: "hard_limit" | "partial" | "manageable";
}

export interface AnalogyCard {
  siteId: string;
  name: string;
  lat: number;
  lon: number;
  targetIds: string[];
  useCaseId: string;
  /** What physical/process similarity transfers */
  transfers: string[];
  /** Where the analogy breaks (links to gaps) */
  breaks: string[];
  /** Concrete tests you would run there */
  tests: string[];
  scaleNotes: string;
  fingerprint: DimensionScore[];
  gaps: GapItem[];
  imageryHints?: { label: string; url: string }[];
}

export interface ValidationReport {
  useCaseId: string;
  targetId: string;
  topFraction: number; // e.g. 0.05
  knownAnalogsInTop: Array<{
    analogId: string;
    rank: number;
    composite: number | null;
  }>;
  passed: boolean;
  notes: string;
}

export interface MethodDoc {
  coarseResolutionDeg: number;
  fineResolutionM: number | null;
  dimensions: Array<{
    key: DimensionKey;
    earthSource: string;
    targetSource: string;
    transform: string; // how normalized
  }>;
  exclusions: string[]; // famous sites removed after validation
  limitations: string[];
}
```

---

## Example fixture sketch (tiny)

Enough for UI wiring before real rasters exist:

```json
{
  "id": "uc_thermal_mobility",
  "title": "Thermal cycling + mobility surface rehearsal",
  "summary": "Find arid, low-vegetation terrain with high diurnal ΔT and traversable slopes for rover thermal/mobility checkout.",
  "body": "both",
  "weights": {
    "diurnal_temp_range": 0.3,
    "slope_roughness": 0.25,
    "precipitation": 0.2,
    "vegetation_ndvi": 0.15,
    "ice_permafrost": 0.1
  },
  "earthLimitsAlways": [
    "Earth gravity ≠ Moon/Mars",
    "Earth atmosphere and radiation environment do not transfer",
    "Biosphere and contamination constraints are Earth-unique"
  ]
}
```

---

## Scoring notes (pipeline contract)

1. Normalize each Earth feature to the same scale as the target feature (z-score within arid mask, or min-max against physically meaningful bounds — **document which**).
2. `similarity = 1 - clip(|e - t| / scale, 0, 1)` or Gaussian kernel; pick one formula and keep it.
3. If `earthValue` or `targetValue` is null → `similarity = null` and exclude that dim from composite (renormalize weights).
4. Always emit per-dimension scores even when composite is null.

---

## Validation set (seed list — refine with citations)

| Name | Approx location | Typical use |
|------|-----------------|-------------|
| Atacama Desert | N Chile | Mars aridity / UV / salts |
| Antarctic Dry Valleys | Antarctica | Cold desert / Mars-like |
| Iceland | Iceland | Volcanic / Moon-Mars geology |
| Hawaiʻi (Mauna Kea / volcanic fields) | Hawaiʻi | Volcanic / regolith analogs |
| *(optional)* Mojave | SW USA | Ops / rover testing heritage |

Exact lat/lon + citations go in `known_analogs.json` on Day 1.
