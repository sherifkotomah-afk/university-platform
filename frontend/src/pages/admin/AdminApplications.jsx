import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import { ADMIN_LINKS } from './AdminDashboard'
import api from '../../api/client'

const STATUSES = ['Under Review', 'Offer Made', 'Accepted', 'Rejected', 'Enrolled']

export default function AdminApplications() {
  const [applications, setApplications] = useState([])
  const [error, setError] = useState('')

  function load() {
    api.get('/applications').then((res) => setApplications(res.data)).catch(() => {})
  }

  useEffect(() => { load() }, [])

  async function decide(id, status) {
    setError('')
    try {
      await api.patch(`/applications/${id}/decision`, { status })
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update decision.')
    }
  }

  return (
    <PortalLayout links={ADMIN_LINKS}>
      <h1>Admissions Review</h1>
      {error && <p className="error-text">{error}</p>}
      <table>
        <thead><tr><th>ID</th><th>Type</th><th>WASSCE Index</th><th>Status</th><th>Action</th></tr></thead>
        <tbody>
          {applications.map((a) => (
            <tr key={a.id}>
              <td>{a.id}</td>
              <td>{a.application_type}</td>
              <td>{a.wassce_index_number || '-'}</td>
              <td>{a.status}</td>
              <td>
                <select onChange={(e) => decide(a.id, e.target.value)} defaultValue="">
                  <option value="" disabled>Set status...</option>
                  {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </PortalLayout>
  )
}
