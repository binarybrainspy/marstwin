import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'
import {
  analogImage,
  formatScore,
  siteImage,
  targetImage,
} from '../../shared/format'
import { CandidateCard } from '../analogy/CandidateCard'

const targetInfo = {
  mars: { short: 'Jezero Crater', sub: 'Mars · Perseverance / MEDA' },
  moon: { short: 'South polar rim', sub: 'Moon · Shackleton vicinity' },
} as const

export function ValidatePage() {
  const { targets, coarse, knownAnalogs, candidates, manifest } = useAppData()
  const [targetId, setTargetId] = useState('mars_jezero_ref')
  const [showControls, setShowControls] = useState(false)

  const target = targets.find((item) => item.id === targetId) ?? targets[0]
  const report = coarse.validation.find(
    (item) => item.targetId === target.id,
  )
  const ranked = useMemo(
    () =>
      coarse.results
        .filter((result) => result.targetId === target.id)
        .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999)),
    [coarse.results, target.id],
  )

  const visible = showControls
    ? ranked
    : ranked.filter((result) => {
        const cell = coarse.cells.find((item) => item.id === result.cellId)
        return !cell?.isKnownAnalog
      })
  const rows = visible.slice(0, 10)
  const targetCards = candidates.filter((card) =>
    card.targetIds.includes(target.id),
  )
  const bestKnownRank = report
    ? Math.min(
        ...report.knownAnalogsInTop.map((item) => item.rank),
        Number.POSITIVE_INFINITY,
      )
    : null

  return (
    <section className="page evidence-page">
      <header className="page-head evidence-head">
        <p className="eyebrow">Reality check</p>
        <h1>Do the famous sites win?</h1>
        <p className="lede">
          Known analogs are the control group. Before trusting a new candidate,
          the screen has to find the places scientists already agree on.
        </p>
        <div className="evidence-targets">
          {targets.map((item) => {
            const itemReport = coarse.validation.find(
              (validation) => validation.targetId === item.id,
            )
            const best = itemReport
              ? Math.min(...itemReport.knownAnalogsInTop.map((hit) => hit.rank))
              : null
            const info = targetInfo[item.body]
            return (
              <button
                type="button"
                key={item.id}
                className={`evidence-target${
                  item.id === target.id ? ' active' : ''
                }`}
                onClick={() => setTargetId(item.id)}
              >
                <img
                  src={targetImage(item.body)}
                  alt={`${item.body} reference imagery`}
                />
                <span className="evidence-target-body">
                  <span className="eyebrow">{info.sub}</span>
                  <strong>{info.short}</strong>
                  <span className="evidence-target-meta">
                    <span
                      className={`pass-badge ${
                        itemReport?.passed ? 'ok' : 'bad'
                      }`}
                    >
                      {itemReport?.passed ? 'Control passed' : 'Check needed'}
                    </span>
                    <span>
                      best known analog #{best ?? '—'}
                    </span>
                  </span>
                </span>
              </button>
            )
          })}
        </div>
      </header>

      <section className="evidence-section">
        <div className="section-head section-head-row">
          <div>
            <p className="eyebrow">Control group · {targetInfo[target.body].short}</p>
            <h2>The sites the literature already knows.</h2>
            <p>
              A pass means at least one known analog lands in the top three of
              twenty. The best result here is #{bestKnownRank ?? '—'}.
            </p>
          </div>
          {report ? (
            <span className={`pass-badge large ${report.passed ? 'ok' : 'bad'}`}>
              {report.passed ? 'Control passed' : 'Needs attention'}
            </span>
          ) : null}
        </div>

        <div className="control-list">
          {[...knownAnalogs]
            .sort((a, b) => {
              const hitA = report?.knownAnalogsInTop.find(
                (hit) => hit.analogId === a.id,
              )
              const hitB = report?.knownAnalogsInTop.find(
                (hit) => hit.analogId === b.id,
              )
              return (hitA?.rank ?? 999) - (hitB?.rank ?? 999)
            })
            .map((analog) => {
              const hit = report?.knownAnalogsInTop.find(
                (item) => item.analogId === analog.id,
              )
              const passed = hit != null && hit.rank <= 3
              return (
                <article className="control-row" key={analog.id}>
                  <img
                    className="control-image"
                    src={analogImage(analog.id, analog.cellId)}
                    alt={`${analog.name} reference imagery`}
                  />
                  <div className="control-body">
                    <p className="eyebrow">
                      {analog.bodies.join(' + ')} analog
                    </p>
                    <h3>{analog.name}</h3>
                    <p>{analog.whyFamous}</p>
                  </div>
                  <div className="control-rank">
                    <strong>#{hit?.rank ?? '—'}</strong>
                    <span>rank</span>
                  </div>
                  <div className="control-score">
                    <strong>{formatScore(hit?.composite)}</strong>
                    <span>match</span>
                  </div>
                  <span
                    className={`control-status${passed ? ' ok' : ''}`}
                  >
                    {passed ? 'In the top 3' : 'Below the cut'}
                  </span>
                </article>
              )
            })}
        </div>
      </section>

      <section className="evidence-section">
        <div className="ranking-head">
          <div>
            <p className="eyebrow">Ranked cells</p>
            <h2>
              {showControls
                ? 'All twenty cells, controls included.'
                : 'What rises when the controls step aside.'}
            </h2>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={showControls}
              onChange={(event) => setShowControls(event.target.checked)}
            />
            <span className="switch-track" aria-hidden="true">
              <span />
            </span>
            Show controls
          </label>
        </div>

        <div className="ranking-list">
          {rows.map((result) => {
            const cell = coarse.cells.find(
              (item) => item.id === result.cellId,
            )
            const card = candidates.find(
              (item) => item.siteId === result.cellId,
            )
            return (
              <div
                className={`ranking-row${
                  cell?.isKnownAnalog ? ' known' : ''
                }`}
                key={result.cellId}
              >
                <span className="ranking-rank">#{result.rank}</span>
                <img
                  className="ranking-thumb"
                  src={siteImage(result.cellId)}
                  alt={`Satellite view of ${
                    cell?.regionHint ?? result.cellId
                  }`}
                  loading="lazy"
                />
                <div className="ranking-name">
                  <strong>{cell?.regionHint ?? result.cellId}</strong>
                  <span>
                    {cell?.isKnownAnalog ? 'Known analog' : 'Earth cell'} ·{' '}
                    {cell?.lat.toFixed(1)}°, {cell?.lon.toFixed(1)}°
                  </span>
                </div>
                <div className="ranking-score">
                  <strong>{formatScore(result.composite)}</strong>
                  <span>match</span>
                </div>
                {card ? (
                  <Link className="row-link" to={`/candidates/${card.siteId}`}>
                    Field card →
                  </Link>
                ) : (
                  <Link
                    className="row-link"
                    to={`/screen?target=${target.id}&cell=${result.cellId}`}
                  >
                    View on map →
                  </Link>
                )}
              </div>
            )
          })}
        </div>
      </section>

      <section className="evidence-section">
        <div className="section-head">
          <p className="eyebrow">New candidates</p>
          <h2>What we would take to the field.</h2>
          <p>
            Candidate cards are generated only after the control group passes.
            Known analogs are never promoted as new sites.
          </p>
        </div>
        {targetCards.length ? (
          <div className="candidate-grid">
            {targetCards.map((card) => (
              <CandidateCard key={card.siteId} card={card} body={target.body} />
            ))}
          </div>
        ) : (
          <p className="panel-note">
            This destination has no promoted field cards yet. The atlas still
            ranks all {manifest.counts.cells} cells above.
          </p>
        )}
      </section>
    </section>
  )
}
