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
  DIMENSION_LABELS,
  type DimensionKey,
  type DimensionScore,
} from '../../shared/types'

export function FingerprintChart({
  scores,
  height = 260,
}: {
  scores: DimensionScore[]
  height?: number
}) {
  const data = scores.map((s) => ({
    key: s.key,
    label: DIMENSION_LABELS[s.key as DimensionKey],
    similarity: s.similarity,
    display: s.similarity == null ? 0 : s.similarity,
    unknown: s.similarity == null,
  }))

  return (
    <div className="fingerprint" style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--grid)" />
          <XAxis
            type="number"
            domain={[0, 1]}
            tick={{ fill: 'var(--muted)', fontSize: 11 }}
          />
          <YAxis
            type="category"
            dataKey="label"
            width={120}
            tick={{ fill: 'var(--text)', fontSize: 11 }}
          />
          <Tooltip
            formatter={(value, _name, item) => {
              const unknown = Boolean(
                (item as { payload?: { unknown?: boolean } })?.payload?.unknown,
              )
              if (unknown) return ['unknown', 'similarity']
              const n = typeof value === 'number' ? value : Number(value)
              return [Number.isFinite(n) ? n.toFixed(2) : '—', 'similarity']
            }}
            contentStyle={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              color: 'var(--text)',
            }}
          />
          <Bar dataKey="display" fill="var(--accent)" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
