import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'

export function ValidatePage() {
  const { usecase, targets, coarse, knownAnalogs, candidates } = useAppData()
  const [targetId, setTargetId] = useState('mars_jezero_ref')
  const [excludeFamous, setExcludeFamous] = useState(true)

  const target = targets.find((t) => t.id === targetId) ?? targets[0]
  const report = coarse.validation.find((v) => v.targetId === target.id)

  const ranked = useMemo(() => {
    return coarse.results
      .filter((r) => r.targetId === target.id && r.useCaseId === usecase.id)
      .sort((a, b) => (a.rank ?? 999) - (b.rank ?? 999))
  }, [coarse.results, target.id, usecase.id])

  const visible = ranked.filter((r) => {
    if (!excludeFamous) return true
    const cell = coarse.cells.find((c) => c.id === r.cellId)
    return !cell?.isKnownAnalog
  })

  return (
    <section className="page">
      <header className="page-head">
        <h1>Validation gate</h1>
        <p>
          Known analogs should rank high for the matching target. Then exclude
          them to surface new hardware-test candidates.
        </p>
        <div className="toggle-row">
          {targets.map((t) => (
            <button
              key={t.id}
              type="button"
              className={t.id === target.id ? 'chip active' : 'chip'}
              onClick={() => setTargetId(t.id)}
            >
              {t.name}
            </button>
          ))}
        </div>
      </header>

      {report ? (
        <div className={`banner ${report.passed ? 'ok' : 'bad'}`}>
          {report.passed ? 'Passed' : 'Needs attention'}: {report.notes}
        </div>
      ) : null}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Analog</th>
              <th>Rank</th>
              <th>Composite</th>
              <th>Why famous</th>
            </tr>
          </thead>
          <tbody>
            {(report?.knownAnalogsInTop ?? []).map((h) => {
              const analog = knownAnalogs.find((a) => a.id === h.analogId)
              return (
                <tr key={h.analogId}>
                  <td>{analog?.name ?? h.analogId}</td>
                  <td>#{h.rank}</td>
                  <td>{h.composite?.toFixed(3) ?? '—'}</td>
                  <td className="muted">{analog?.whyFamous}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <label className="check">
        <input
          type="checkbox"
          checked={excludeFamous}
          onChange={(e) => setExcludeFamous(e.target.checked)}
        />
        Exclude famous sites
      </label>

      <h2>Remaining candidates</h2>
      <ol className="rank-list">
        {visible.slice(0, 5).map((r) => {
          const cell = coarse.cells.find((c) => c.id === r.cellId)
          const card = candidates.find((c) => c.siteId === r.cellId)
          return (
            <li key={r.cellId}>
              <strong>{cell?.regionHint ?? r.cellId}</strong>
              <span className="muted">
                {' '}
                · rank #{r.rank} · {r.composite?.toFixed(2)}
              </span>
              {card ? (
                <>
                  {' '}
                  <Link to={`/candidates/${card.siteId}`}>Open card</Link>
                </>
              ) : null}
            </li>
          )
        })}
      </ol>
    </section>
  )
}
