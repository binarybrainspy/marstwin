import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  SHORT_DIMENSION_LABELS,
  dimensionLabel,
} from '../../shared/format'
import type { DimensionKey, DimensionScore } from '../../shared/types'

export function FingerprintChart({
  scores,
  height = 240,
}: {
  scores: DimensionScore[]
  height?: number
}) {
  const data = scores.map((score) => ({
    key: score.key,
    label: SHORT_DIMENSION_LABELS[score.key as DimensionKey],
    display: score.similarity == null ? 0 : score.similarity,
    unknown: score.similarity == null,
  }))

  return (
    <div className="fingerprint" style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 2, right: 18, bottom: 2, left: 0 }}
          barCategoryGap={7}
        >
          <CartesianGrid
            horizontal={false}
            strokeDasharray="2 4"
            stroke="var(--grid)"
          />
          <XAxis
            type="number"
            domain={[0, 1]}
            ticks={[0, 0.5, 1]}
            tick={{ fill: 'var(--faint)', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={64}
            tick={{ fill: 'var(--text)', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: 'rgba(244, 236, 226, 0.04)' }}
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
          <Bar
            dataKey="display"
            fill="var(--accent)"
            radius={[0, 2, 2, 0]}
            barSize={9}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
