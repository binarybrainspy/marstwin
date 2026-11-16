import {
  DIMENSION_LABELS,
  type DimensionKey,
  type DimensionScore,
} from './types'

export const SHORT_DIMENSION_LABELS: Record<DimensionKey, string> = {
  slope_roughness: 'Slope',
  diurnal_temp_range: 'ΔT',
  precipitation: 'Rain',
  vegetation_ndvi: 'NDVI',
  mineralogy: 'Minerals',
  ice_permafrost: 'Ice',
}

export function siteImage(cellId: string) {
  return `/images/sites/${cellId}.jpg`
}

export function targetImage(body: 'moon' | 'mars') {
  return `/images/target-${body}.jpg`
}

export function analogImage(analogId?: string, cellId?: string) {
  if (analogId === 'ka_atacama') return '/images/analog-atacama.jpg'
  if (analogId === 'ka_dry_valleys') return '/images/analog-dry-valleys.jpg'
  if (cellId) return siteImage(cellId)
  return '/images/world.jpg'
}

export function formatDate(iso: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return date.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

export function formatScore(value: number | null | undefined) {
  if (value == null) return '—'
  return Math.round(value * 100).toString()
}

export function formatDimensionValue(
  key: DimensionKey,
  value: number | null | undefined,
) {
  if (value == null) return '—'
  switch (key) {
    case 'slope_roughness':
      return `${value.toFixed(1)}°`
    case 'diurnal_temp_range':
      return `${value.toFixed(0)} K`
    case 'precipitation':
      return `${value.toFixed(0)} mm/yr`
    case 'vegetation_ndvi':
      return value.toFixed(3)
    case 'mineralogy':
    case 'ice_permafrost':
      return value.toFixed(2)
  }
}

export function scoreFor(scores: DimensionScore[], key: DimensionKey) {
  return scores.find((score) => score.key === key)
}

export function earthValue(
  scores: DimensionScore[],
  key: DimensionKey,
): number | null {
  return scoreFor(scores, key)?.earthValue ?? null
}

export function strongestSignals(scores: DimensionScore[], limit = 3) {
  return scores
    .filter(
      (score): score is DimensionScore & { similarity: number } =>
        score.similarity != null,
    )
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, limit)
}

export function dimensionLabel(key: DimensionKey) {
  return DIMENSION_LABELS[key]
}

export function bestRankFor(
  validation: Array<{
    targetId: string
    knownAnalogsInTop: Array<{ analogId: string; rank: number }>
  }>,
  analogId: string,
) {
  return validation
    .map((report) => {
      const hit = report.knownAnalogsInTop.find((item) => item.analogId === analogId)
      if (!hit) return null
      return {
        targetId: report.targetId,
        rank: hit.rank,
      }
    })
    .filter((item): item is { targetId: string; rank: number } => item != null)
}
