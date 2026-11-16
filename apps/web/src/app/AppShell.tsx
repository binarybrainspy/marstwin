import { useEffect } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAppData } from './DataProvider'
import { formatDate } from '../shared/format'

const links = [
  { to: '/', label: 'Overview', end: true },
  { to: '/screen', label: 'Atlas' },
  { to: '/validate', label: 'Reality check' },
  { to: '/method', label: 'Method' },
]

export function AppShell() {
  const { manifest } = useAppData()
  const location = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
  }, [location.pathname])

  return (
    <div className="shell">
      <header className="topbar">
        <NavLink to="/" className="brand" aria-label="MarsTwin home">
          <span className="brand-mark" aria-hidden="true">
            <span />
          </span>
          <span className="brand-copy">
            <span className="brand-name">MarsTwin</span>
            <span className="brand-sub">Analog Earth Atlas</span>
          </span>
        </NavLink>

        <nav className="nav" aria-label="Primary">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                isActive ? 'nav-link active' : 'nav-link'
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <Link className="data-chip" to="/method" title="Open the data manifest">
          <span className="dot" aria-hidden="true" />
          DATA · {formatDate(manifest.generatedAt)}
        </Link>
      </header>

      <main className="main">
        <Outlet />
      </main>

      <footer className="footer">
        <div className="footer-grid">
          <div className="footer-brand">
            <p className="footer-wordmark">MarsTwin</p>
            <p>
              An analog Earth atlas for testing surface hardware and operations
              against the Moon and Mars.
            </p>
            <p className="muted">Built for NASA Space Apps 2026.</p>
          </div>

          <div className="footer-meta">
            <p className="eyebrow">Dataset</p>
            <p>
              {manifest.counts.cells} sites · {manifest.counts.targets}{' '}
              destinations · generated {formatDate(manifest.generatedAt)}
            </p>
            <p className="muted">
              Pipeline v{manifest.pipelineVersion} · {manifest.ndvi.product}{' '}
              {manifest.ndvi.year} · slopes {manifest.slope.status}
            </p>
            <Link to="/method">Method, provenance and sources →</Link>
          </div>

          <div className="footer-credit">
            <p className="eyebrow">Credits</p>
            <p>{manifest.imagery.credits}</p>
            <p className="muted">
              NASA POWER · ORNL DAAC · USGS Astrogeology · NASA MEDA · NASA
              Image Library
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
