import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import { FACULTY_LINKS } from './FacultyDashboard'
import api from '../../api/client'

const COMPONENT_TYPES = ['CAT1', 'CAT2', 'Assignment', 'Exam']

export default function FacultyCourseManage() {
  const { id } = useParams() // course_assignment_id
  const [roster, setRoster] = useState([])
  const [error, setError] = useState('')
  const [scoreForm, setScoreForm] = useState({}) // keyed by course_registration_id

  function loadRoster() {
    api.get(`/faculty/me/courses/${id}/roster`).then((res) => setRoster(res.data)).catch(() => {})
  }

  useEffect(() => { loadRoster() }, [id])

  function updateForm(regId, field, value) {
    setScoreForm((f) => ({ ...f, [regId]: { ...f[regId], [field]: value } }))
  }

  async function submitComponent(regId) {
    setError('')
    const entry = scoreForm[regId] || {}
    try {
      await api.post('/faculty/me/assessment-components', {
        course_registration_id: regId,
        component_type: entry.component_type || 'CAT1',
        max_score: parseFloat(entry.max_score || 100),
        score: parseFloat(entry.score || 0),
        weight_percent: parseFloat(entry.weight_percent || 10),
      })
      alert('Score saved.')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save score.')
    }
  }

  async function submitFinalGrade(regId) {
    const entry = scoreForm[regId] || {}
    try {
      const res = await api.post('/faculty/me/submit-final-grade', {
        course_registration_id: regId,
        total_score: parseFloat(entry.total_score || 0),
      })
      alert(`Final grade submitted: ${res.data.letter_grade} (pending registrar approval)`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit final grade.')
    }
  }

  return (
    <PortalLayout links={FACULTY_LINKS}>
      <h1>Course Roster & Gradebook</h1>
      {error && <p className="error-text">{error}</p>}

      {roster.map((s) => (
        <div key={s.course_registration_id} className="card">
          <h3>{s.first_name} {s.last_name} ({s.student_id_number})</h3>

          <div className="grid cols-4">
            <div>
              <label>Component</label>
              <select onChange={(e) => updateForm(s.course_registration_id, 'component_type', e.target.value)}>
                {COMPONENT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label>Score</label>
              <input type="number" onChange={(e) => updateForm(s.course_registration_id, 'score', e.target.value)} />
            </div>
            <div>
              <label>Max Score</label>
              <input type="number" defaultValue={100} onChange={(e) => updateForm(s.course_registration_id, 'max_score', e.target.value)} />
            </div>
            <div>
              <label>Weight %</label>
              <input type="number" defaultValue={10} onChange={(e) => updateForm(s.course_registration_id, 'weight_percent', e.target.value)} />
            </div>
          </div>
          <button className="btn secondary" onClick={() => submitComponent(s.course_registration_id)}>Save Component Score</button>

          <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <label style={{ margin: 0 }}>Final Score:</label>
            <input type="number" style={{ maxWidth: '100px' }} onChange={(e) => updateForm(s.course_registration_id, 'total_score', e.target.value)} />
            <button className="btn" onClick={() => submitFinalGrade(s.course_registration_id)}>Submit Final Grade</button>
          </div>
        </div>
      ))}
      {roster.length === 0 && <p>No students registered yet.</p>}
    </PortalLayout>
  )
}
