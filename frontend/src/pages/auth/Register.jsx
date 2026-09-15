import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../../components/Navbar'

export default function Register() {
  const { registerApplicant } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await registerApplicant(form)
      navigate('/applicant/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>Create Applicant Account</h1>
        <form onSubmit={handleSubmit}>
          <div>
            <label>First Name</label>
            <input value={form.first_name} onChange={(e) => update('first_name', e.target.value)} required />
          </div>
          <div>
            <label>Last Name</label>
            <input value={form.last_name} onChange={(e) => update('last_name', e.target.value)} required />
          </div>
          <div>
            <label>Email</label>
            <input type="email" value={form.email} onChange={(e) => update('email', e.target.value)} required />
          </div>
          <div>
            <label>Phone</label>
            <input value={form.phone} onChange={(e) => update('phone', e.target.value)} />
          </div>
          <div>
            <label>Password (min 8 characters)</label>
            <input type="password" minLength={8} value={form.password} onChange={(e) => update('password', e.target.value)} required />
          </div>
          {error && <p className="error-text">{error}</p>}
          <button className="btn" type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <p style={{ marginTop: '1rem' }}>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  )
}
