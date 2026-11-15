import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/screen', label: 'Screen' },
  { to: '/validate', label: 'Validate' },
  { to: '/method', label: 'Method' },
]

export function AppShell() {
  return (
    <div className="shell">
      <header className="topbar">
        <NavLink to="/" className="brand">
          MarsTwin
        </NavLink>
        <nav className="nav">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.end}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="main">
        <Outlet />
      </main>
    </div>
  )
}
