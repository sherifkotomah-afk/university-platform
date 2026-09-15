import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

export const ADMIN_LINKS = [
  { to: '/admin/dashboard', label: 'Overview' },
  { to: '/admin/applications', label: 'Admissions' },
  { to: '/admin/grades', label: 'Grade Approvals' },
]

export default function AdminDashboard() {
  const [pendingApps, setPendingApps] = useState([])
  const [pendingGrades, setPendingGrades] = useState([])

  useEffect(() => {
    api.get('/applications', { params: { status_filter: 'Submitted' } }).then((res) => setPendingApps(res.data)).catch(() => {})
    api.get('/admin/final-grades/pending-approval').then((res) => setPendingGrades(res.data)).catch(() => {})
  }, [])

  return (
    <PortalLayout links={ADMIN_LINKS}>
      <h1>Admin Overview</h1>
      <div className="grid cols-2">
        <div className="card stat-card">
          <div className="value">{pendingApps.length}</div>
          <div className="label">Applications Awaiting Review</div>
        </div>
        <div className="card stat-card">
          <div className="value">{pendingGrades.length}</div>
          <div className="label">Grades Awaiting Approval</div>
        </div>
      </div>
    </PortalLayout>
  )
}
