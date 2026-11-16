import { useAppData } from '../../app/DataProvider'
import { formatDate, dimensionLabel } from '../../shared/format'
import type { DimensionKey } from '../../shared/types'

const blankNotes = [
  {
    title: 'Slopes are pending',
    body: 'Every site waits on the same 20 m baseline. A coarser Earth DEM is flagged, not quietly substituted.',
  },
  {
    title: 'The Moon has no air ΔT',
    body: 'The polar reference is illumination-driven. The lunar diurnal value stays null instead of borrowing an Earth day–night number.',
  },
  {
    title: 'Mineralogy is blank',
    body: 'No citable site mineralogy is locked yet, so the dimension is excluded and weighted at zero.',
  },
  {
    title: 'One vegetation gap remains',
    body: 'MODIS returns no coverage for the Dry Valleys. The cell is shown as unknown, not filled with a guess.',
  },
  {
    title: 'Ice is a proxy',
    body: 'Ice and permafrost values are coarse screening proxies until a proper Odyssey-informed layer is wired in.',
  },
]

export function MethodPage() {
  const { method, usecase, targets, manifest } = useAppData()

  return (
    <section className="page method-page">
      <header className="page-head">
        <p className="eyebrow">Method & provenance</p>
        <h1>A screen, not a verdict.</h1>
        <p className="lede">
          MarsTwin compares six measurable signals, keeps the nulls visible, and
          validates against sites the literature already knows. The result is a
          shortlist to investigate — not a site-selection decision.
        </p>
      </header>

      <section className="provenance">
        <div className="provenance-item">
          <span className="eyebrow">Data run</span>
          <strong>{formatDate(manifest.generatedAt)}</strong>
          <span>Pipeline v{manifest.pipelineVersion}</span>
        </div>
        <div className="provenance-item">
          <span className="eyebrow">Vegetation</span>
          <strong>{manifest.ndvi.product}</strong>
          <span>
            {manifest.ndvi.year} · {manifest.counts.ndviWithData}/
            {manifest.counts.cells} cells
          </span>
        </div>
        <div className="provenance-item">
          <span className="eyebrow">Slope baseline</span>
          <strong>{manifest.slope.baselineM} m</strong>
          <span>{manifest.slope.status} · {manifest.counts.slopesComputed} cells</span>
        </div>
        <div className="provenance-item">
          <span className="eyebrow">Controls</span>
          <strong>{manifest.counts.knownAnalogs} known analogs</strong>
          <span>
            {manifest.validation.filter((item) => item.passed).length}/
            {manifest.validation.length} targets pass
          </span>
        </div>
      </section>

      <section className="method-section">
        <p className="eyebrow">The short version</p>
        <h2>How the ranking is built.</h2>
        <div className="method-steps">
          <div>
            <span className="step-number">01</span>
            <h3>Build a fingerprint</h3>
            <p>
              Six dimensions: slope, air-temperature swing, rainfall,
              vegetation, mineralogy and ice. Each has a named source and a null
              when the observation is not ready.
            </p>
          </div>
          <div>
            <span className="step-number">02</span>
            <h3>Weight for the use case</h3>
            <p>
              The thermal and mobility use case weights the dimensions
              differently. The composite is a screening aid; the six-dimension
              fingerprint is the real output.
            </p>
          </div>
          <div>
            <span className="step-number">03</span>
            <h3>Validate, then exclude</h3>
            <p>
              Known analogs are scored first. A target passes when at least one
              lands in the top three of twenty. Then the controls are removed and
              new candidates are promoted.
            </p>
          </div>
        </div>
        <div className="weight-row">
          {Object.entries(usecase.weights).map(([key, weight]) => (
            <span className="weight-pill" key={key}>
              {dimensionLabel(key as DimensionKey)}
              <strong>{Math.round(weight * 100)}%</strong>
            </span>
          ))}
        </div>
      </section>

      <section className="method-section">
        <p className="eyebrow">Six signals</p>
        <h2>What goes in, and what does not.</h2>
        <div className="table-wrap method-table">
          <table>
            <thead>
              <tr>
                <th>Dimension</th>
                <th>Earth source</th>
                <th>Target source</th>
                <th>Transform</th>
              </tr>
            </thead>
            <tbody>
              {method.dimensions.map((dimension) => (
                <tr key={dimension.key}>
                  <td>{dimensionLabel(dimension.key)}</td>
                  <td>{dimension.earthSource}</td>
                  <td>{dimension.targetSource}</td>
                  <td className="muted">{dimension.transform}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="method-section">
        <p className="eyebrow">Deliberate blanks</p>
        <h2>What we refuse to invent.</h2>
        <div className="blank-grid">
          {blankNotes.map((note) => (
            <article className="blank-card" key={note.title}>
              <h3>{note.title}</h3>
              <p>{note.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="method-section">
        <p className="eyebrow">Validation rule</p>
        <h2>The control group decides.</h2>
        <div className="validation-list">
          {manifest.validation.map((report) => {
            const target = targets.find((item) => item.id === report.targetId)
            return (
              <div className="validation-row" key={report.targetId}>
                <span className={`pass-badge ${report.passed ? 'ok' : 'bad'}`}>
                  {report.passed ? 'Pass' : 'Check'}
                </span>
                <div>
                  <strong>{target?.name ?? report.targetId}</strong>
                  <p>{report.notes}</p>
                </div>
              </div>
            )
          })}
        </div>
      </section>

      <section className="method-section">
        <p className="eyebrow">Limitations</p>
        <h2>What this screen cannot tell you.</h2>
        <ul className="plain-list">
          {method.limitations.map((limitation) => (
            <li key={limitation}>{limitation}</li>
          ))}
        </ul>
      </section>

      <section className="method-section sources-section">
        <p className="eyebrow">Provenance</p>
        <h2>Sources behind the manifest.</h2>
        <div className="source-list">
          {manifest.sources.map((source) => (
            <a
              className="source-item"
              key={source.id}
              href={source.url}
              target="_blank"
              rel="noreferrer"
            >
              <span>
                <strong>{source.name}</strong>
                <span>{source.role}</span>
              </span>
              <span aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
        <p className="panel-note">
          The frontend reads <code>manifest.json</code>, generated by pipeline
          v{manifest.pipelineVersion}. Technical notes and report material ship
          with the repository.
        </p>
      </section>
    </section>
  )
}
