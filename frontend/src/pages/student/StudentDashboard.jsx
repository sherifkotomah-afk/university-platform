import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

export const STUDENT_LINKS = [
  { to: '/student/dashboard', label: 'Dashboard' },
  { to: '/student/registration', label: 'Course Registration' },
  { to: '/student/fees', label: 'Fees & Payments' },
  { to: '/student/results', label: 'Results & Transcript' },
]

export default function StudentDashboard() {
  const [profile, setProfile] = useState(null)
  const [invoices, setInvoices] = useState([])
  const [transcript, setTranscript] = useState(null)

  useEffect(() => {
    api.get('/students/me').then((res) => setProfile(res.data)).catch(() => {})
    api.get('/fees/invoices/mine').then((res) => setInvoices(res.data)).catch(() => {})
    api.get('/students/me/transcript').then((res) => setTranscript(res.data)).catch(() => {})
  }, [])

  const outstanding = invoices.reduce((sum, inv) => sum + (inv.total_amount - inv.amount_paid), 0)

  return (
    <PortalLayout links={STUDENT_LINKS}>
      <h1>My Dashboard</h1>

      {profile?.registration_hold && (
        <div className="card" style={{ borderColor: '#c62828', background: '#fdecea' }}>
          <strong>Registration Hold:</strong> {profile.hold_reason || 'Contact the registrar/finance office.'}
        </div>
      )}

      <div className="grid cols-4">
        <div className="card stat-card">
          <div className="value">{profile?.student_id_number || '-'}</div>
          <div className="label">Student ID</div>
        </div>
        <div className="card stat-card">
          <div className="value">{transcript ? transcript.overall_value : '-'}</div>
          <div className="label">{transcript?.grading_system || 'GPA'}</div>
        </div>
        <div className="card stat-card">
          <div className="value">{transcript?.total_credit_hours_completed || 0}</div>
          <div className="label">Credit Hours Completed</div>
        </div>
        <div className="card stat-card">
          <div className="value">GHS {outstanding.toFixed(2)}</div>
          <div className="label">Outstanding Balance</div>
        </div>
      </div>

      <div className="card">
        <h3>Programme Status</h3>
        <p>Year {profile?.current_year_level} · Status: {profile?.status}</p>
      </div>
    </PortalLayout>
  )
}
