import { useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'
import { useAppData } from '../../app/DataProvider'
import { FingerprintChart } from '../fingerprint/FingerprintChart'

export function ScreenPage() {
  const { usecase, targets, coarse, candidates } = useAppData()
  const [params, setParams] = useSearchParams()
  const targetId = params.get('target') ?? 'mars_arid_ref'
  const cellId = params.get('cell')
  const [viewState, setViewState] = useState({
    longitude: 20,
    latitude: 10,
    zoom: 1.4,
  })

  const target = targets.find((t) => t.id === targetId) ?? targets[0]
  const results = useMemo(
    () =>
      coarse.results
        .filter((r) => r.targetId === target.id && r.useCaseId === usecase.id)
        .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999)),
    [coarse.results, target.id, usecase.id],
  )

  const selected =
    results.find((r) => r.cellId === cellId) ?? results[0] ?? null
  const selectedCell = coarse.cells.find((c) => c.id === selected?.cellId)
  const isCandidate = candidates.some((c) => c.siteId === selected?.cellId)

  return (
    <section className="split">
      <div className="map-wrap">
        <Map
          {...viewState}
          onMove={(e) => setViewState(e.viewState)}
          mapStyle="https://demotiles.maplibre.org/style.json"
          style={{ width: '100%', height: '100%' }}
        >
          <NavigationControl position="top-right" />
          {coarse.cells.map((cell) => {
            const rank = results.find((r) => r.cellId === cell.id)?.rank
            const active = cell.id === selected?.cellId
            return (
              <Marker
                key={cell.id}
                longitude={cell.lon}
                latitude={cell.lat}
                anchor="center"
                onClick={(e) => {
                  e.originalEvent.stopPropagation()
                  const next = new URLSearchParams(params)
                  next.set('cell', cell.id)
                  next.set('target', target.id)
                  setParams(next)
                }}
              >
                <button
                  type="button"
                  className={`pin${active ? ' active' : ''}${cell.isKnownAnalog ? ' known' : ''}`}
                  title={`${cell.regionHint ?? cell.id}${rank ? ` · #${rank}` : ''}`}
                >
                  {rank ?? '·'}
                </button>
              </Marker>
            )
          })}
        </Map>
      </div>

      <aside className="side">
        <div className="side-head">
          <h1>Coarse screen</h1>
          <p className="muted">{usecase.title}</p>
          <div className="toggle-row">
            {targets.map((t) => (
              <button
                key={t.id}
                type="button"
                className={t.id === target.id ? 'chip active' : 'chip'}
                onClick={() => {
                  const next = new URLSearchParams(params)
                  next.set('target', t.id)
                  setParams(next)
                }}
              >
                {t.body === 'moon' ? 'Moon' : 'Mars'}
              </button>
            ))}
          </div>
        </div>

        {selected && selectedCell ? (
          <>
            <h2>{selectedCell.regionHint ?? selectedCell.id}</h2>
            <p className="meta">
              rank #{selected.rank} · composite{' '}
              {selected.composite?.toFixed(2) ?? '—'} · {selectedCell.lat.toFixed(1)}°,{' '}
              {selectedCell.lon.toFixed(1)}°
              {selectedCell.isKnownAnalog ? ' · known analog' : ''}
            </p>
            <FingerprintChart scores={selected.dimensions} />
            <div className="cta-row">
              <Link className="btn ghost" to="/validate">
                Run validation
              </Link>
              {isCandidate ? (
                <Link
                  className="btn primary"
                  to={`/candidates/${selected.cellId}`}
                >
                  Analogy card
                </Link>
              ) : null}
            </div>
          </>
        ) : (
          <p>No results — re-run the pipeline.</p>
        )}
      </aside>
    </section>
  )
}
