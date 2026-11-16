import { Link } from 'react-router-dom'
import { useAppData } from '../../app/DataProvider'
import {
  analogImage,
  bestRankFor,
  formatDate,
  siteImage,
  targetImage,
} from '../../shared/format'
import { CandidateCard } from '../analogy/CandidateCard'

const targetCopy = {
  mars: {
    kicker: 'Mars · Jezero Crater',
    name: 'The rover benchmark',
    line: 'A concrete rover site: strong day–night air swings, no rain, barren ground.',
    image: targetImage('mars'),
  },
  moon: {
    kicker: 'Moon · South polar rim',
    name: 'The hard limit',
    line: 'Permanent shadow and cold traps sit outside anything Earth can reproduce.',
    image: targetImage('moon'),
  },
} as const

const steps = [
  {
    title: 'Measure what can be measured',
    body: 'Slope, air-temperature swing, rainfall, vegetation, mineralogy and ice — each with a source, and a null when it is not ready.',
  },
  {
    title: 'Score each destination separately',
    body: 'The same Earth site can be a good Mars analog and a poor Moon analog. The screen never collapses them into one ranking.',
  },
  {
    title: 'Check the controls',
    body: 'Known analogs are the test. If Atacama and the Dry Valleys do not rise, the screen has failed.',
  },
  {
    title: 'Publish the gap',
    body: 'Every field card separates what transfers from what never will — gravity, atmosphere, radiation and scale.',
  },
]

export function HomePage() {
  const { usecase, candidates, targets, knownAnalogs, coarse, manifest } =
    useAppData()
  const topCandidate = candidates[0]
  const orderedTargets = [...targets].sort((a, b) =>
    a.body === 'mars' ? -1 : b.body === 'mars' ? 1 : 0,
  )

  return (
    <div className="home">
      <section className="hero">
        <img
          className="hero-bg"
          src={targetImage('mars')}
          alt=""
          aria-hidden="true"
        />
        <div className="hero-shade" />
        <div className="hero-inner">
          <div className="hero-copy">
            <p className="eyebrow">
              NASA Space Apps 2026 · Analog Earth Locations
            </p>
            <h1 className="hero-title">
              The closest thing to Mars{' '}
              <em>is still Earth.</em>
            </h1>
            <p className="lede">
              MarsTwin screens twenty of Earth&apos;s driest, coldest and most
              barren landscapes against Jezero Crater and the lunar south pole.
              It shows where the comparison holds — and where it breaks.
            </p>
            <div className="cta-row">
              <Link className="btn primary" to={`/screen?usecase=${usecase.id}`}>
                Explore the atlas <span aria-hidden="true">→</span>
              </Link>
              <Link className="btn ghost" to="/validate">
                See the reality check
              </Link>
            </div>
            <div className="hero-stats">
              <div className="stat">
                <strong>{manifest.counts.cells}</strong>
                <span>Earth sites</span>
              </div>
              <div className="stat">
                <strong>{manifest.counts.targets}</strong>
                <span>destinations</span>
              </div>
              <div className="stat">
                <strong>6</strong>
                <span>signals compared</span>
              </div>
              <div className="stat">
                <strong>{manifest.counts.knownAnalogs}</strong>
                <span>control sites</span>
              </div>
            </div>
            <p className="dataset-line">
              Data run {formatDate(manifest.generatedAt)} ·{' '}
              {manifest.counts.ndviWithData}/{manifest.counts.cells} sites with
              measured vegetation · slopes pending
            </p>
          </div>

          {topCandidate ? (
            <Link
              className="hero-inset"
              to={`/candidates/${topCandidate.siteId}`}
            >
              <div className="inset-media">
                <img
                  src={siteImage(topCandidate.siteId)}
                  alt={`Satellite view of ${topCandidate.name}`}
                />
                <span className="inset-label">Earth · new candidate</span>
              </div>
              <div className="inset-body">
                <p className="eyebrow">
                  #{topCandidate.rank} of {manifest.counts.cells} · Mars analog
                </p>
                <h2>{topCandidate.name}</h2>
                <p>{topCandidate.headline}</p>
                <span className="text-link">
                  Open field card <span aria-hidden="true">→</span>
                </span>
              </div>
            </Link>
          ) : null}
        </div>
      </section>

      <section className="section targets-section">
        <div className="section-head">
          <p className="eyebrow">Two destinations</p>
          <h2>One atlas. Two very different targets.</h2>
          <p>
            A site that rehearses a rover sol on Mars can be a poor stand-in for
            a shadowed lunar pole. The screen keeps the two cases apart.
          </p>
        </div>
        <div className="target-grid">
          {orderedTargets.map((target) => {
            const copy = targetCopy[target.body]
            const temperature =
              target.features.diurnal_temp_range?.value ?? null
            const rain = target.features.precipitation?.value ?? null
            const slope = target.features.slope_roughness?.value ?? null
            return (
              <Link
                key={target.id}
                className={`target-card ${target.body}`}
                to={`/screen?target=${target.id}`}
              >
                <div className="target-media">
                  <img src={copy.image} alt={`${target.body} reference imagery`} />
                  <span className="media-kicker">{target.body}</span>
                  <span className="target-arrow">View atlas →</span>
                </div>
                <div className="target-body">
                  <p className="eyebrow">{copy.kicker}</p>
                  <h3>{copy.name}</h3>
                  <p>{copy.line}</p>
                  <div className="target-stats">
                    <div>
                      <strong>
                        {temperature == null ? 'No lock' : `${temperature} K`}
                      </strong>
                      <span>air swing</span>
                    </div>
                    <div>
                      <strong>{rain == null ? '—' : `${rain} mm`}</strong>
                      <span>rain / yr</span>
                    </div>
                    <div>
                      <strong>{slope == null ? 'Pending' : `${slope}°`}</strong>
                      <span>20 m slope</span>
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
        <p className="section-note">
          The lunar comparison is deliberately incomplete: no Earth surface
          reaches the ~40 K cold-trap regime, so the gap is reported instead of
          scored away.
        </p>
      </section>

      <section className="section">
        <div className="section-head section-head-row">
          <div>
            <p className="eyebrow">New candidates</p>
            <h2>Sites that survive the screen.</h2>
            <p>
              These are the highest-ranked sites left after the famous analogs
              are removed from the candidate pool.
            </p>
          </div>
          <Link className="text-link" to="/validate">
            How they were picked <span aria-hidden="true">→</span>
          </Link>
        </div>
        {candidates.length ? (
          <div className="candidate-grid">
            {candidates.map((card) => (
              <CandidateCard key={card.siteId} card={card} />
            ))}
          </div>
        ) : (
          <p className="muted">No new candidates have been generated yet.</p>
        )}
      </section>

      <section className="section controls-section">
        <div className="section-head">
          <p className="eyebrow">Reality check</p>
          <h2>The famous sites still win.</h2>
          <p>
            Known analogs are the control group. If the screen cannot find them,
            it cannot be trusted with a new site.
          </p>
        </div>
        <div className="analog-grid">
          {knownAnalogs.map((analog) => {
            const ranks = bestRankFor(coarse.validation, analog.id).sort(
              (a, b) => a.rank - b.rank,
            )
            return (
              <article className="analog-card" key={analog.id}>
                <div className="analog-media">
                  <img
                    src={analogImage(analog.id, analog.cellId)}
                    alt={`${analog.name} reference imagery`}
                    loading="lazy"
                  />
                  {ranks[0] ? (
                    <span className="rank-badge">Best #{ranks[0].rank}</span>
                  ) : null}
                </div>
                <div className="analog-body">
                  <p className="eyebrow">{analog.bodies.join(' + ')}</p>
                  <h3>{analog.name}</h3>
                  <p>{analog.whyFamous}</p>
                  <div className="analog-ranks">
                    {ranks.map((rank) => {
                      const target = targets.find(
                        (item) => item.id === rank.targetId,
                      )
                      return (
                        <span className="rank-pill" key={rank.targetId}>
                          {target?.body ?? 'target'} #{rank.rank}
                        </span>
                      )
                    })}
                  </div>
                </div>
              </article>
            )
          })}
        </div>
        <div className="section-action">
          <Link className="btn ghost" to="/validate">
            Open the reality check
          </Link>
        </div>
      </section>

      <section className="section method-band">
        <div className="section-head">
          <p className="eyebrow">How it works</p>
          <h2>Four moves. No magic score.</h2>
        </div>
        <div className="step-grid">
          {steps.map((step, index) => (
            <article className="step" key={step.title}>
              <span className="step-number">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="usecase-band">
        <div className="usecase-band-inner">
          <div>
            <p className="eyebrow">The test question</p>
            <h2>{usecase.title}</h2>
            <p>
              Can an Earth desert rehearse the thermal and mobility load of a
              rover sol? The atlas answers that without pretending Earth is
              Mars.
            </p>
          </div>
          <Link className="btn ghost" to="/method">
            How the screen works <span aria-hidden="true">→</span>
          </Link>
        </div>
      </section>
    </div>
  )
}
