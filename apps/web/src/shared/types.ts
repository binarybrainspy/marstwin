/** Six locked dimensions — no optional dims for solo scope */
export const DIMENSION_KEYS = [
  'slope_roughness',
  'diurnal_temp_range',
  'precipitation',
  'vegetation_ndvi',
  'mineralogy',
  'ice_permafrost',
] as const

export type DimensionKey = (typeof DIMENSION_KEYS)[number]

export const DIMENSION_LABELS: Record<DimensionKey, string> = {
  slope_roughness: 'Slope / roughness',
  diurnal_temp_range: 'Diurnal ΔT',
  precipitation: 'Precipitation',
  vegetation_ndvi: 'Vegetation (NDVI)',
  mineralogy: 'Mineralogy',
  ice_permafrost: 'Ice / permafrost',
}

export interface UseCase {
  id: string
  title: string
  summary: string
  body: 'moon' | 'mars' | 'both'
  weights: Record<DimensionKey, number>
  earthLimitsAlways: string[]
}

export interface CitedValue {
  value: number | null
  unit: string
  source: string
  sourceUrl?: string
  notes?: string
}

export interface TargetProfile {
  id: string
  body: 'moon' | 'mars'
  name: string
  lat: number
  lon: number
  rationale: string
  features: Partial<Record<DimensionKey, CitedValue>>
}

export interface EarthCell {
  id: string
  lat: number
  lon: number
  cellDeg: number
  features: Partial<Record<DimensionKey, number | null>>
  regionHint?: string
  isKnownAnalog?: boolean
  knownAnalogId?: string
}

export interface DimensionScore {
  key: DimensionKey
  similarity: number | null
  earthValue: number | null
  targetValue: number | null
  note?: string
}

export interface SimilarityResult {
  cellId: string
  targetId: string
  useCaseId: string
  dimensions: DimensionScore[]
  composite: number | null
  rank?: number
}

export interface KnownAnalog {
  id: string
  name: string
  lat: number
  lon: number
  whyFamous: string
  bodies: Array<'moon' | 'mars'>
  cellId?: string
}

export interface GapItem {
  id: string
  category:
    | 'gravity'
    | 'atmosphere_vacuum'
    | 'radiation'
    | 'magnetic'
    | 'biosphere'
    | 'scale'
    | 'temporal'
    | 'logistics'
    | 'other'
  title: string
  detail: string
  severity: 'hard_limit' | 'partial' | 'manageable'
}

export interface AnalogyCard {
  siteId: string
  name: string
  lat: number
  lon: number
  targetIds: string[]
  useCaseId: string
  transfers: string[]
  breaks: string[]
  tests: string[]
  scaleNotes: string
  fingerprint: DimensionScore[]
  gaps: GapItem[]
}

export interface ValidationReport {
  useCaseId: string
  targetId: string
  topFraction: number
  knownAnalogsInTop: Array<{
    analogId: string
    rank: number
    composite: number | null
  }>
  passed: boolean
  notes: string
}

export interface MethodDoc {
  coarseResolutionDeg: number
  fineResolutionM: number | null
  dimensions: Array<{
    key: DimensionKey
    earthSource: string
    targetSource: string
    transform: string
  }>
  exclusions: string[]
  limitations: string[]
}

export interface CoarseBundle {
  cells: EarthCell[]
  results: SimilarityResult[]
  validation: ValidationReport[]
}
