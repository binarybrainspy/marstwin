import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import {
  SHORT_DIMENSION_LABELS,
  dimensionLabel,
} from '../../shared/format'
import type { DimensionKey, DimensionScore } from '../../shared/types'

export function FingerprintRadar({
  scores,
  height = 280,
}: {
  scores: DimensionScore[]
  height?: number
}) {
  const data = scores.map((score) => ({
    key: score.key,
    label: SHORT_DIMENSION_LABELS[score.key as DimensionKey],
    value: score.similarity ?? 0,
    unknown: score.similarity == null,
  }))

  return (
    <div className="radar" style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <RadarChart data={data} outerRadius="70%">
          <PolarGrid stroke="var(--grid)" />
          <PolarAngleAxis
            dataKey="label"
            tick={{ fill: 'var(--muted)', fontSize: 11 }}
          />
          <PolarRadiusAxis domain={[0, 1]} tick={false} axisLine={false} />
          <Radar
            dataKey="value"
            stroke="var(--accent)"
            fill="var(--accent)"
            fillOpacity={0.24}
            strokeWidth={2}
          />
          <Tooltip
            formatter={(value, _name, item) => {
              const payload = (
                item as { payload?: { unknown?: boolean; key?: string } }
              )?.payload
              if (payload?.unknown) return ['unknown', 'similarity']
              const n = typeof value === 'number' ? value : Number(value)
              const label = payload?.key
                ? dimensionLabel(payload.key as DimensionKey)
                : 'Similarity'
              return [Number.isFinite(n) ? n.toFixed(2) : '—', label]
            }}
            contentStyle={{
              background: 'var(--surface-solid)',
              border: '1px solid var(--border)',
              borderRadius: 2,
              color: 'var(--text)',
              fontFamily: 'var(--mono)',
              fontSize: 11,
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
