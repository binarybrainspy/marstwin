import { Link, useParams } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'
import {
  earthValue,
  formatDate,
  formatDimensionValue,
  formatScore,
  dimensionLabel,
  siteImage,
  targetImage,
} from '../../shared/format'
import type { DimensionKey } from '../../shared/types'
import { FingerprintRadar } from '../fingerprint/FingerprintRadar'
import { ScoreRing } from '../fingerprint/ScoreRing'

const targetCaption = {
  mars: { label: 'Mars · Jezero Crater', note: 'Reference target · Perseverance / MEDA' },
  moon: { label: 'Moon · South polar rim', note: 'Reference target · Shackleton vicinity' },
} as const

export function CandidatePage() {
  const { id } = useParams()
  const { candidates, targets, coarse, usecase, manifest } = useAppData()
  const card = candidates.find((item) => item.siteId === id)

  if (!card) {
    return (
      <section className="page narrow">
        <p className="eyebrow">Field card</p>
        <h1>Candidate not found</h1>
        <p className="muted">
          This site has not been promoted to a field card yet.
        </p>
        <Link className="btn ghost" to="/validate">
          Back to the reality check
        </Link>
      </section>
    )
  }

  const target = targets.find((item) => item.id === card.targetIds[0])
  const body = target?.body ?? 'mars'
  const copy = targetCaption[body]
  const cell = coarse.cells.find((item) => item.id === card.siteId)
  const temperature = earthValue(card.fingerprint, 'diurnal_temp_range')
  const ndvi = earthValue(card.fingerprint, 'vegetation_ndvi')
  const slope = earthValue(card.fingerprint, 'slope_roughness')

  return (
    <article className="page field-page">
      <header className="field-head">
        <p className="eyebrow">
          Field card · {body} analog candidate
        </p>
        <h1>{card.name}</h1>
        <p className="field-headline">{card.headline}</p>
        <p className="lede">{card.story}</p>
        <div className="badge-row">
          <span className={`body-badge ${body}`}>{body} analog</span>
          <span className="tag">Rank #{card.rank ?? '—'} of {manifest.counts.cells}</span>
          <span className="tag">Use case: {usecase.title}</span>
        </div>
      </header>

      <div className="field-medias">
        <div className="field-media earth">
          <img
            src={siteImage(card.siteId)}
            alt={`Satellite view of ${card.name}`}
          />
          <div className="media-overlay">
            <span className="media-kicker">Earth · site context</span>
            <div>
              <strong>{card.name}</strong>
              <span>
                {card.lat.toFixed(2)}°, {card.lon.toFixed(2)}°
              </span>
            </div>
          </div>
          <div className="media-score">
            <ScoreRing value={card.composite} size={92} />
          </div>
        </div>

        <div className="field-media target">
          <img src={targetImage(body)} alt={`${body} reference imagery`} />
          <div className="media-overlay">
            <span className="media-kicker">{copy.label}</span>
            <div>
              <strong>{target?.name ?? copy.label}</strong>
              <span>{copy.note}</span>
            </div>
          </div>
          <span className="target-stamp">
            {body === 'mars' ? 'MARS' : 'MOON'}
          </span>
        </div>
      </div>

      <div className="field-stats">
        <div>
          <strong>#{card.rank ?? '—'}</strong>
          <span>rank of {manifest.counts.cells}</span>
        </div>
        <div>
          <strong>{formatScore(card.composite)}</strong>
          <span>match / 100</span>
        </div>
        <div>
          <strong>{formatDimensionValue('diurnal_temp_range', temperature)}</strong>
          <span>air swing</span>
        </div>
        <div>
          <strong>{formatDimensionValue('vegetation_ndvi', ndvi)}</strong>
          <span>NDVI</span>
        </div>
        <div>
          <strong>
            {slope == null
              ? 'Pending'
              : formatDimensionValue('slope_roughness', slope)}
          </strong>
          <span>20 m slope</span>
        </div>
      </div>

      <div className="field-layout">
        <div className="field-main">
          <section className="field-section">
            <p className="eyebrow">01 · What carries over</p>
            <h2>Why this site earns a closer look.</h2>
            <ul className="bullet-list">
              {card.transfers.map((transfer) => (
                <li key={transfer}>
                  <span className="bullet-icon ok">✓</span>
                  <span>{transfer}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="field-section">
            <p className="eyebrow">02 · What we would test</p>
            <h2>A field plan, not a photo op.</h2>
            <ul className="bullet-list">
              {card.tests.map((test) => (
                <li key={test}>
                  <span className="bullet-icon test">→</span>
                  <span>{test}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="field-section">
            <p className="eyebrow">03 · Where the analogy breaks</p>
            <h2>The parts Earth cannot rehearse.</h2>
            <ul className="bullet-list">
              {card.breaks.map((item) => (
                <li key={item}>
                  <span className="bullet-icon break">!</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </section>

          <section className="field-section">
            <p className="eyebrow">04 · Gap report</p>
            <h2>What a test campaign must carry with it.</h2>
            <div className="gap-list">
              {card.gaps.map((gap) => (
                <article className={`gap ${gap.severity}`} key={gap.id}>
                  <div className="gap-head">
                    <h3>{gap.title}</h3>
                    <span className="tag">
                      {gap.severity.replace('_', ' ')}
                    </span>
                  </div>
                  <p>{gap.detail}</p>
                </article>
              ))}
            </div>
          </section>
        </div>

        <aside className="field-aside">
          <div className="panel-card">
            <p className="eyebrow">Fingerprint</p>
            <h3>Six signals, one shape.</h3>
            <FingerprintRadar scores={card.fingerprint} height={250} />
            <p className="panel-note">
              Unmeasured dimensions sit at the centre. They are excluded from the
              match, not scored as zero.
            </p>
          </div>

          <div className="panel-card">
            <p className="eyebrow">Signal by signal</p>
            <h3>Earth → {body === 'mars' ? 'Mars' : 'Moon'}.</h3>
            <div className="dimension-list">
              {card.fingerprint.map((score) => {
                const key = score.key as DimensionKey
                const similarity =
                  score.similarity == null
                    ? null
                    : Math.round(score.similarity * 100)
                return (
                  <div className="dimension-row" key={key}>
                    <div className="dimension-head">
                      <span>{dimensionLabel(key)}</span>
                      <span>{similarity == null ? 'unknown' : `${similarity}%`}</span>
                    </div>
                    <div className="dimension-values">
                      <span>{formatDimensionValue(key, score.earthValue)}</span>
                      <span className="arrow" aria-hidden="true">
                        →
                      </span>
                      <span>{formatDimensionValue(key, score.targetValue)}</span>
                    </div>
                    <div className="dimension-bar">
                      <span style={{ width: `${similarity ?? 0}%` }} />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          <div className="panel-card">
            <p className="eyebrow">At a glance</p>
            <h3>Field notes.</h3>
            <dl className="fact-list">
              <div>
                <dt>Target</dt>
                <dd>{target?.name ?? copy.label}</dd>
              </div>
              <div>
                <dt>Cell</dt>
                <dd>
                  ~{cell?.cellDeg ?? 0.5}° screen cell at{' '}
                  {card.lat.toFixed(1)}°, {card.lon.toFixed(1)}°
                </dd>
              </div>
              <div>
                <dt>Vegetation</dt>
                <dd>
                  MODIS 250 m sample, {manifest.ndvi.year}
                  {ndvi == null ? ' (no coverage)' : ''}
                </dd>
              </div>
              <div>
                <dt>Slope</dt>
                <dd>
                  {slope == null
                    ? `Pending shared ${manifest.slope.baselineM} m baseline`
                    : formatDimensionValue('slope_roughness', slope)}
                </dd>
              </div>
              <div>
                <dt>Thermal path</dt>
                <dd>Air ↔ air only (POWER vs MEDA)</dd>
              </div>
            </dl>
          </div>

          <div className="panel-card target-note">
            <p className="eyebrow">Target rationale</p>
            <p>{target?.rationale}</p>
          </div>
        </aside>
      </div>

      <footer className="field-foot">
        <p className="panel-note">{card.scaleNotes}</p>
        <p className="panel-note">
          Data run {formatDate(manifest.generatedAt)} · MODIS NDVI{' '}
          {manifest.ndvi.year} · pipeline {manifest.pipelineVersion}
        </p>
        <Link className="btn ghost" to={`/screen?target=${target?.id ?? ''}&cell=${card.siteId}`}>
          Back to the atlas
        </Link>
      </footer>
    </article>
  )
}
