import { useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Map, {
  Marker,
  NavigationControl,
  ScaleControl,
  type MapRef,
} from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useAppData } from '../../app/DataProvider'
import {
  dimensionLabel,
  earthValue,
  formatDimensionValue,
  formatScore,
  siteImage,
  strongestSignals,
} from '../../shared/format'
import { FingerprintChart } from '../fingerprint/FingerprintChart'
import { ScoreRing } from '../fingerprint/ScoreRing'
import { atlasStyle, type BaseLayer } from './atlasStyle'

const INITIAL_VIEW = {
  longitude: 18,
  latitude: 12,
  zoom: 1.35,
}

export function ScreenPage() {
  const { usecase, targets, coarse, candidates, manifest } = useAppData()
  const [params, setParams] = useSearchParams()
  const targetId = params.get('target') ?? 'mars_jezero_ref'
  const cellId = params.get('cell')
  const [baseLayer, setBaseLayer] = useState<BaseLayer>('satellite')
  const [mapError, setMapError] = useState(false)
  const mapRef = useRef<MapRef | null>(null)

  const target = targets.find((item) => item.id === targetId) ?? targets[0]
  const results = useMemo(
    () =>
      coarse.results
        .filter(
          (result) =>
            result.targetId === target.id && result.useCaseId === usecase.id,
        )
        .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999)),
    [coarse.results, target.id, usecase.id],
  )

  const fallback =
    results.find((result) =>
      candidates.some((card) => card.siteId === result.cellId),
    ) ??
    results[0] ??
    null
  const selected =
    results.find((result) => result.cellId === cellId) ?? fallback
  const selectedCell = coarse.cells.find(
    (cell) => cell.id === selected?.cellId,
  )
  const selectedCard = candidates.find(
    (card) => card.siteId === selected?.cellId,
  )
  const style = useMemo(() => atlasStyle(baseLayer), [baseLayer])

  const chooseCell = (id: string, lon: number, lat: number) => {
    const next = new URLSearchParams(params)
    next.set('cell', id)
    next.set('target', target.id)
    setParams(next)
    mapRef.current?.flyTo({
      center: [lon, lat],
      zoom: 4.1,
      duration: 1200,
      essential: true,
    })
  }

  const chooseTarget = (id: string) => {
    const next = new URLSearchParams(params)
    next.set('target', id)
    setParams(next)
  }

  return (
    <section className="atlas-layout">
      <div className="map-stage">
        <Map
          ref={mapRef}
          initialViewState={INITIAL_VIEW}
          mapStyle={style}
          maxZoom={18}
          minZoom={1}
          onError={() => setMapError(true)}
          style={{ width: '100%', height: '100%' }}
        >
          <NavigationControl position="bottom-right" showCompass={false} />
          <ScaleControl position="bottom-left" unit="metric" />
          {coarse.cells.map((cell) => {
            const rank = results.find(
              (result) => result.cellId === cell.id,
            )?.rank
            const active = cell.id === selected?.cellId
            return (
              <Marker
                key={cell.id}
                longitude={cell.lon}
                latitude={cell.lat}
                anchor="center"
                onClick={(event) => {
                  event.originalEvent.stopPropagation()
                  chooseCell(cell.id, cell.lon, cell.lat)
                }}
              >
                <button
                  type="button"
                  className={`pin${active ? ' active' : ''}${
                    cell.isKnownAnalog ? ' known' : ''
                  }`}
                  title={`${cell.regionHint ?? cell.id}${
                    rank ? ` · rank ${rank}` : ''
                  }`}
                  aria-label={`Select ${cell.regionHint ?? cell.id}`}
                >
                  {rank ?? '·'}
                </button>
              </Marker>
            )
          })}
        </Map>

        <div className="map-overlay-top">
          <div className="map-title">
            <p className="eyebrow">Analog atlas</p>
            <h1>Find the closest match.</h1>
            <p>
              {manifest.counts.cells} Earth cells ranked for{' '}
              {target.body === 'mars' ? 'Mars' : 'the Moon'}.
            </p>
          </div>
          <div className="map-controls">
            <div className="map-toggle" aria-label="Destination">
              {targets.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={item.id === target.id ? 'active' : ''}
                  aria-pressed={item.id === target.id}
                  onClick={() => chooseTarget(item.id)}
                >
                  {item.body === 'mars' ? 'Mars' : 'Moon'}
                </button>
              ))}
            </div>
            <div className="map-toggle" aria-label="Map layer">
              <button
                type="button"
                className={baseLayer === 'satellite' ? 'active' : ''}
                aria-pressed={baseLayer === 'satellite'}
                onClick={() => setBaseLayer('satellite')}
              >
                Satellite
              </button>
              <button
                type="button"
                className={baseLayer === 'terrain' ? 'active' : ''}
                aria-pressed={baseLayer === 'terrain'}
                onClick={() => setBaseLayer('terrain')}
              >
                Terrain
              </button>
            </div>
          </div>
        </div>

        <div className="map-legend">
          <span>
            <i className="legend-dot candidate" /> New candidate
          </span>
          <span>
            <i className="legend-dot known" /> Known analog
          </span>
          <span>
            <i className="legend-dot selected" /> Selected
          </span>
        </div>

        {mapError ? (
          <div className="map-error">
            Map imagery could not load. Site cards and scores still work.
          </div>
        ) : null}
      </div>

      <aside className="atlas-side">
        {selected && selectedCell ? (
          <>
            <div className="side-head">
              <p className="eyebrow">Selected cell</p>
              <h2>{selectedCell.regionHint ?? selectedCell.id}</h2>
              <p className="meta">
                #{selected.rank} of {manifest.counts.cells} ·{' '}
                {selectedCell.lat.toFixed(1)}°, {selectedCell.lon.toFixed(1)}°
              </p>
              <div className="badge-row">
                <span className={`body-badge ${target.body}`}>
                  {target.body} analog
                </span>
                {selectedCell.isKnownAnalog ? (
                  <span className="tag known-tag">Known analog</span>
                ) : selectedCard ? (
                  <span className="tag">New candidate</span>
                ) : null}
              </div>
            </div>

            <div className="site-photo">
              <img
                src={siteImage(selectedCell.id)}
                alt={`Satellite view of ${
                  selectedCell.regionHint ?? selectedCell.id
                }`}
              />
              <span className="image-label">Earth · satellite context</span>
              <div className="score-overlay">
                <ScoreRing value={selected.composite} size={84} />
              </div>
            </div>

            <div className="stat-grid">
              <div className="stat-tile">
                <strong>
                  {formatDimensionValue(
                    'diurnal_temp_range',
                    earthValue(selected.dimensions, 'diurnal_temp_range'),
                  )}
                </strong>
                <span>air swing</span>
              </div>
              <div className="stat-tile">
                <strong>
                  {formatDimensionValue(
                    'vegetation_ndvi',
                    earthValue(selected.dimensions, 'vegetation_ndvi'),
                  )}
                </strong>
                <span>NDVI</span>
              </div>
              <div className="stat-tile">
                <strong>
                  {formatDimensionValue(
                    'precipitation',
                    earthValue(selected.dimensions, 'precipitation'),
                  )}
                </strong>
                <span>rain / yr</span>
              </div>
              <div className="stat-tile">
                <strong>
                  {earthValue(selected.dimensions, 'slope_roughness') == null
                    ? 'Pending'
                    : formatDimensionValue(
                        'slope_roughness',
                        earthValue(selected.dimensions, 'slope_roughness'),
                      )}
                </strong>
                <span>20 m slope</span>
              </div>
            </div>

            <div className="panel-section">
              <div className="panel-heading">
                <h3>Signal match</h3>
                <span>{formatScore(selected.composite)} / 100</span>
              </div>
              <FingerprintChart scores={selected.dimensions} height={190} />
            </div>

            <div className="panel-section">
              <h3>Strongest signals</h3>
              <div className="signal-grid">
                {strongestSignals(selected.dimensions, 3).map((signal) => (
                  <span className="signal-chip" key={signal.key}>
                    <span>{dimensionLabel(signal.key)}</span>
                    <strong>{Math.round(signal.similarity * 100)}%</strong>
                  </span>
                ))}
              </div>
            </div>

            <div className="panel-actions">
              {selectedCard ? (
                <Link
                  className="btn primary"
                  to={`/candidates/${selectedCard.siteId}`}
                >
                  Open field card <span aria-hidden="true">→</span>
                </Link>
              ) : null}
              <Link className="btn ghost" to="/validate">
                Reality check
              </Link>
            </div>

            <div className="panel-section top-list">
              <div className="panel-heading">
                <h3>Top of the screen</h3>
                <span>{target.body}</span>
              </div>
              {results.slice(0, 5).map((result) => {
                const cell = coarse.cells.find(
                  (item) => item.id === result.cellId,
                )
                const active = result.cellId === selected.cellId
                return (
                  <button
                    key={result.cellId}
                    type="button"
                    className={`top-row${active ? ' active' : ''}`}
                    onClick={() => {
                      if (cell) chooseCell(cell.id, cell.lon, cell.lat)
                    }}
                  >
                    <span className="top-rank">#{result.rank}</span>
                    <span className="top-name">
                      {cell?.regionHint ?? result.cellId}
                      {cell?.isKnownAnalog ? (
                        <em className="top-known">known</em>
                      ) : null}
                    </span>
                    <span className="top-score">
                      {formatScore(result.composite)}
                    </span>
                  </button>
                )
              })}
            </div>

            <p className="panel-note">
              MODIS NDVI {manifest.ndvi.year} · air ΔT from NASA POWER ·
              slopes {manifest.slope.status}
            </p>
          </>
        ) : (
          <p>No results — re-run the pipeline.</p>
        )}
      </aside>
    </section>
  )
}
