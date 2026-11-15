import { Link } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'

export function HomePage() {
  const { usecase, candidates } = useAppData()

  return (
    <section className="hero-page">
      <p className="eyebrow">NASA Space Apps · Analog Earth Locations</p>
      <h1 className="hero-brand">MarsTwin</h1>
      <p className="lede">
        Hardware-test first: find Earth sites for thermal cycling and mobility
        rehearsal, score them on six physical dimensions, then say plainly where
        the Moon/Mars analogy breaks.
      </p>
      <div className="cta-row">
        <Link className="btn primary" to={`/screen?usecase=${usecase.id}`}>
          Start from use case
        </Link>
        <Link className="btn ghost" to="/validate">
          Validation gate
        </Link>
      </div>
      <div className="usecase-panel">
        <h2>{usecase.title}</h2>
        <p>{usecase.summary}</p>
        {candidates[0] ? (
          <p className="muted">
            Top new candidate stub:{' '}
            <Link to={`/candidates/${candidates[0].siteId}`}>
              {candidates[0].name}
            </Link>
          </p>
        ) : null}
      </div>
    </section>
  )
}
