import type { StyleSpecification } from 'maplibre-gl'

export type BaseLayer = 'satellite' | 'terrain'

const EARTH_IMAGERY =
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
const SHADED_RELIEF =
  'https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}'
const PLACE_LABELS =
  'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'

export function atlasStyle(base: BaseLayer): StyleSpecification {
  return {
    version: 8,
    sources: {
      base: {
        type: 'raster',
        tiles: [base === 'satellite' ? EARTH_IMAGERY : SHADED_RELIEF],
        tileSize: 256,
        maxzoom: 19,
        attribution:
          base === 'satellite'
            ? 'Imagery © Esri, Maxar, Earthstar Geographics'
            : 'Relief © Esri',
      },
      labels: {
        type: 'raster',
        tiles: [PLACE_LABELS],
        tileSize: 256,
        maxzoom: 19,
        attribution: 'Labels © Esri',
      },
    },
    layers: [
      {
        id: 'background',
        type: 'background',
        paint: {
          'background-color': '#0b0908',
        },
      },
      {
        id: 'base',
        type: 'raster',
        source: 'base',
        paint: {
          'raster-saturation': base === 'satellite' ? -0.08 : -0.25,
          'raster-contrast': 0.04,
        },
      },
      {
        id: 'labels',
        type: 'raster',
        source: 'labels',
        paint: {
          'raster-opacity': 0.68,
        },
      },
    ],
  }
}
