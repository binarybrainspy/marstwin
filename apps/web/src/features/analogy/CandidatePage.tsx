import { Link, useParams } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'
import { FingerprintChart } from '../fingerprint/FingerprintChart'

export function CandidatePage() {
  const { id } = useParams()
  const { candidates, usecase } = useAppData()
  const card = candidates.find((c) => c.siteId === id)

  if (!card) {
    return (
      <section className="page">
        <h1>Candidate not found</h1>
        <Link to="/validate">Back to validation</Link>
      </section>
    )
  }

  return (
    <section className="page narrow">
      <p className="eyebrow">Analogy card · {usecase.title}</p>
      <h1>{card.name}</h1>
      <p className="meta">
        {card.lat.toFixed(2)}°, {card.lon.toFixed(2)}° · targets:{' '}
        {card.targetIds.join(', ')}
      </p>

      <FingerprintChart scores={card.fingerprint} height={240} />

      <div className="columns">
        <div>
          <h2>What transfers</h2>
          <ul>
            {card.transfers.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
        <div>
          <h2>Where it breaks</h2>
          <ul>
            {card.breaks.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ul>
        </div>
      </div>

      <h2>What you would test here</h2>
      <ul>
        {card.tests.map((t) => (
          <li key={t}>{t}</li>
        ))}
      </ul>

      <h2>Gap report</h2>
      <ul className="gaps">
        {card.gaps.map((g) => (
          <li key={g.id} className={`gap ${g.severity}`}>
            <strong>{g.title}</strong>
            <span className="tag">{g.severity.replace('_', ' ')}</span>
            <p>{g.detail}</p>
          </li>
        ))}
      </ul>

      <p className="muted">{card.scaleNotes}</p>
      <Link className="btn ghost" to="/screen">
        Back to map
      </Link>
    </section>
  )
}
