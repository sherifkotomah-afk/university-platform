import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { BRAND } from '../config/brand'
import ThemeToggle from './ThemeToggle'

export default function PortalLayout({ links, children }) {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div>
      <nav className="navbar">
        <Link to="/" className="brand">{BRAND.institutionName}</Link>
        <div>
          <span style={{ marginRight: '1.5rem' }}>
            {user?.first_name} {user?.last_name} ({user?.role})
          </span>
          <button className="btn secondary" onClick={logout}>Logout</button>
          <ThemeToggle />
        </div>
      </nav>
      <div className="sidebar-layout">
        <aside className="sidebar">
          {links.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={location.pathname === link.to ? 'active' : ''}
            >
              {link.label}
            </Link>
          ))}
        </aside>
        <main className="main-content">{children}</main>
      </div>
    </div>
  )
}
