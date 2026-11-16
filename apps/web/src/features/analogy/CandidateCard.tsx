import { Link } from 'react-router-dom'
import {
  earthValue,
  formatDimensionValue,
  siteImage,
} from '../../shared/format'
import type { AnalogyCard } from '../../shared/types'
import { ScoreRing } from '../fingerprint/ScoreRing'

export function CandidateCard({
  card,
  body = 'mars',
}: {
  card: AnalogyCard
  body?: 'moon' | 'mars'
}) {
  const temperature = earthValue(card.fingerprint, 'diurnal_temp_range')
  const ndvi = earthValue(card.fingerprint, 'vegetation_ndvi')
  const slope = earthValue(card.fingerprint, 'slope_roughness')

  return (
    <Link className="candidate-card" to={`/candidates/${card.siteId}`}>
      <div className="candidate-media">
        <img
          src={siteImage(card.siteId)}
          alt={`Satellite view of ${card.name}`}
          loading="lazy"
        />
        <div className="candidate-badges">
          <span className="rank-badge">#{card.rank ?? '—'} of 20</span>
          <span className={`body-badge ${body}`}>{body} analog</span>
        </div>
        <div className="candidate-score">
          <ScoreRing value={card.composite} size={72} />
        </div>
      </div>
      <div className="candidate-body">
        <p className="eyebrow">New candidate · {body}</p>
        <h3>{card.name}</h3>
        <p className="candidate-headline">{card.headline}</p>
        <p className="candidate-story">{card.story}</p>
        <div className="candidate-metrics">
          <span>
            <strong>{formatDimensionValue('diurnal_temp_range', temperature)}</strong>
            day–night swing
          </span>
          <span>
            <strong>{formatDimensionValue('vegetation_ndvi', ndvi)}</strong>
            NDVI
          </span>
          <span>
            <strong>
              {slope == null ? 'Pending' : formatDimensionValue('slope_roughness', slope)}
            </strong>
            20 m slope
          </span>
        </div>
        <span className="text-link">
          Open field card <span aria-hidden="true">→</span>
        </span>
      </div>
    </Link>
  )
}
