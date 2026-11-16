import type { CSSProperties } from 'react'

export function ScoreRing({
  value,
  label = 'match',
  size = 96,
}: {
  value: number | null | undefined
  label?: string
  size?: number
}) {
  const percent = value == null ? null : Math.round(value * 100)
  return (
    <div
      className={`score-ring${percent == null ? ' empty' : ''}`}
      style={
        {
          '--score': `${(percent ?? 0) * 3.6}deg`,
          width: size,
          height: size,
        } as CSSProperties
      }
      aria-label={
        percent == null ? `Match unknown` : `Match ${percent} out of 100`
      }
    >
      <div className="score-ring-inner">
        <strong>{percent == null ? '—' : percent}</strong>
        <span>{label}</span>
      </div>
    </div>
  )
}
