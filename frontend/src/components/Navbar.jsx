import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { BRAND } from '../config/brand'
import ThemeToggle from './ThemeToggle'

const DASHBOARD_PATH = {
  applicant: '/applicant/dashboard',
  student: '/student/dashboard',
  faculty: '/faculty/dashboard',
  admin: '/admin/dashboard',
  registrar: '/admin/dashboard',
  finance: '/admin/dashboard',
}

export default function Navbar() {
  const { user } = useAuth()

  return (
    <nav className="navbar">
      <Link to="/" className="brand">{BRAND.institutionName}</Link>
      <div>
        <Link to="/academics">Academics</Link>
        <Link to="/admissions">Admissions</Link>
        <Link to="/news">News</Link>
        <Link to="/contact">Contact</Link>
        {user ? (
          <Link to={DASHBOARD_PATH[user.role] || '/'}>My Dashboard</Link>
        ) : (
          <Link to="/login">Login</Link>
        )}
        <ThemeToggle />
      </div>
    </nav>
  )
}
