import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

const LINKS = [
  { to: '/applicant/dashboard', label: 'Dashboard' },
  { to: '/applicant/apply', label: 'Apply' },
]

const STATUS_COLOR = {
  Submitted: 'yellow', 'Under Review': 'yellow', 'Offer Made': 'green',
  Accepted: 'green', Enrolled: 'green', Rejected: 'red',
}

export default function ApplicantDashboard() {
  const [applications, setApplications] = useState([])

  useEffect(() => {
    api.get('/applications/mine').then((res) => setApplications(res.data)).catch(() => {})
  }, [])

  return (
    <PortalLayout links={LINKS}>
      <h1>My Applications</h1>
      {applications.length === 0 && (
        <div className="card">
          <p>You haven't submitted an application yet.</p>
          <Link to="/applicant/apply" className="btn">Start Application</Link>
        </div>
      )}
      {applications.map((app) => (
        <div key={app.id} className="card">
          <h3>Application #{app.id} — {app.application_type}</h3>
          <p>
            Status: <span className={`badge ${STATUS_COLOR[app.status] || 'gray'}`}>{app.status}</span>
          </p>
          {app.decision_notes && <p>Notes: {app.decision_notes}</p>}
          <Link to={`/applicant/applications/${app.id}`}>View details & documents</Link>
        </div>
      ))}
    </PortalLayout>
  )
}
