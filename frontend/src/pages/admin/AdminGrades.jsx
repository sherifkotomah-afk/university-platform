import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import { ADMIN_LINKS } from './AdminDashboard'
import api from '../../api/client'

export default function AdminGrades() {
  const [pending, setPending] = useState([])
  const [error, setError] = useState('')

  function load() {
    api.get('/admin/final-grades/pending-approval').then((res) => setPending(res.data)).catch(() => {})
  }

  useEffect(() => { load() }, [])

  async function approve(courseRegId) {
    setError('')
    try {
      await api.patch(`/admin/final-grades/${courseRegId}/approve`)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not approve grade.')
    }
  }

  return (
    <PortalLayout links={ADMIN_LINKS}>
      <h1>Grade Approvals</h1>
      {error && <p className="error-text">{error}</p>}
      <table>
        <thead><tr><th>Course Reg. ID</th><th>Score</th><th>Letter</th><th>Grade Point</th><th></th></tr></thead>
        <tbody>
          {pending.map((g) => (
            <tr key={g.course_registration_id}>
              <td>{g.course_registration_id}</td>
              <td>{g.total_score}</td>
              <td>{g.letter_grade}</td>
              <td>{g.grade_point}</td>
              <td><button className="btn" onClick={() => approve(g.course_registration_id)}>Approve & Release</button></td>
            </tr>
          ))}
          {pending.length === 0 && <tr><td colSpan={5}>No grades pending approval.</td></tr>}
        </tbody>
      </table>
    </PortalLayout>
  )
}
