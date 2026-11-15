import { useAppData } from '../../app/DataProvider'
import { DIMENSION_LABELS, type DimensionKey } from '../../shared/types'

export function MethodPage() {
  const { method, usecase } = useAppData()

  return (
    <section className="page narrow">
      <h1>Method</h1>
      <p>
        Coarse screen at ~{method.coarseResolutionDeg}°, use-case-weighted
        fingerprint (not a single magic score), validate on known analogs, then
        exclude them. Hardware-test narrative: <em>{usecase.title}</em>.
      </p>

      <h2>Six dimensions</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Dimension</th>
              <th>Earth</th>
              <th>Target</th>
              <th>Transform</th>
            </tr>
          </thead>
          <tbody>
            {method.dimensions.map((d) => (
              <tr key={d.key}>
                <td>{DIMENSION_LABELS[d.key as DimensionKey]}</td>
                <td>{d.earthSource}</td>
                <td>{d.targetSource}</td>
                <td className="muted">{d.transform}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2>Exclusions after validation</h2>
      <ul>
        {method.exclusions.map((e) => (
          <li key={e}>{e}</li>
        ))}
      </ul>

      <h2>Limitations</h2>
      <ul>
        {method.limitations.map((e) => (
          <li key={e}>{e}</li>
        ))}
      </ul>
    </section>
  )
}
