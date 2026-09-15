import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import { STUDENT_LINKS } from './StudentDashboard'
import api from '../../api/client'

export default function StudentResults() {
  const [transcript, setTranscript] = useState(null)
  const [requesting, setRequesting] = useState(false)
  const [requests, setRequests] = useState([])
  const [message, setMessage] = useState('')

  function load() {
    api.get('/students/me/transcript').then((res) => setTranscript(res.data)).catch(() => {})
    api.get('/students/me/transcript-requests').then((res) => setRequests(res.data)).catch(() => {})
  }

  useEffect(() => { load() }, [])

  async function requestTranscript(type) {
    setRequesting(true)
    setMessage('')
    try {
      await api.post('/students/me/transcript-requests', { request_type: type })
      setMessage(`${type} transcript requested.`)
      load()
    } catch (err) {
      setMessage(err.response?.data?.detail || 'Could not submit request.')
    } finally {
      setRequesting(false)
    }
  }

  async function appeal(courseRegId) {
    const reason = window.prompt('Reason for grade appeal:')
    if (!reason) return
    try {
      await api.post('/students/me/grade-appeals', { course_registration_id: courseRegId, reason })
      alert('Appeal submitted.')
    } catch (err) {
      alert(err.response?.data?.detail || 'Could not submit appeal.')
    }
  }

  return (
    <PortalLayout links={STUDENT_LINKS}>
      <h1>Results & Transcript</h1>

      <div className="card">
        <h3>Cumulative {transcript?.grading_system || 'GPA'}: {transcript?.overall_value ?? '-'}</h3>
        <p>Total credit hours completed: {transcript?.total_credit_hours_completed ?? 0}</p>
      </div>

      <table>
        <thead>
          <tr><th>Course</th><th>Credit Hours</th><th>Score</th><th>Grade</th><th></th></tr>
        </thead>
        <tbody>
          {transcript?.results.map((r) => (
            <tr key={r.course_registration_id}>
              <td>{r.course_code} — {r.course_title}</td>
              <td>{r.credit_hours}</td>
              <td>{r.final_grade?.total_score ?? 'Pending'}</td>
              <td>{r.final_grade?.letter_grade ?? '-'}</td>
              <td>
                {r.final_grade?.total_score != null && (
                  <button className="btn secondary" onClick={() => appeal(r.course_registration_id)}>Appeal</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Transcript Requests</h2>
      <div className="card">
        <button className="btn" onClick={() => requestTranscript('Unofficial')} disabled={requesting}>
          Request Unofficial Transcript
        </button>{' '}
        <button className="btn secondary" onClick={() => requestTranscript('Official')} disabled={requesting}>
          Request Official Transcript
        </button>
        {message && <p style={{ marginTop: '0.5rem' }}>{message}</p>}
        <table style={{ marginTop: '1rem' }}>
          <thead><tr><th>Type</th><th>Status</th></tr></thead>
          <tbody>
            {requests.map((r) => (
              <tr key={r.id}><td>{r.request_type}</td><td>{r.status}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </PortalLayout>
  )
}
