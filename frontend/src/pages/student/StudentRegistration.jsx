import { useEffect, useState } from 'react'
import PortalLayout from '../../components/PortalLayout'
import { STUDENT_LINKS } from './StudentDashboard'
import api from '../../api/client'

export default function StudentRegistration() {
  const [profile, setProfile] = useState(null)
  const [programmeCourses, setProgrammeCourses] = useState([])
  const [myRegistrations, setMyRegistrations] = useState([])
  const [academicYear, setAcademicYear] = useState('2026/2027')
  const [semester, setSemester] = useState(1)
  const [error, setError] = useState('')

  function loadRegistrations() {
    api.get('/students/me/registrations', { params: { academic_year: academicYear, semester } })
      .then((res) => setMyRegistrations(res.data)).catch(() => {})
  }

  useEffect(() => {
    api.get('/students/me').then((res) => {
      setProfile(res.data)
      api.get(`/academics/programmes/${res.data.programme_id}`).then((p) => setProgrammeCourses(p.data.courses))
    }).catch(() => {})
  }, [])

  useEffect(() => { loadRegistrations() }, [academicYear, semester])

  async function registerCourse(courseId) {
    setError('')
    try {
      await api.post('/students/me/register-course', { course_id: courseId, academic_year: academicYear, semester })
      loadRegistrations()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not register for this course.')
    }
  }

  async function dropCourse(regId) {
    try {
      await api.delete(`/students/me/registrations/${regId}`)
      loadRegistrations()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not drop this course.')
    }
  }

  const registeredCourseIds = new Set(myRegistrations.filter((r) => r.status === 'Registered').map((r) => r.course_id))

  return (
    <PortalLayout links={STUDENT_LINKS}>
      <h1>Course Registration</h1>

      {profile?.registration_hold && (
        <div className="card" style={{ borderColor: '#c62828', background: '#fdecea' }}>
          Registration is blocked: {profile.hold_reason || 'contact the registrar/finance office.'}
        </div>
      )}

      <div className="card">
        <div className="grid cols-2">
          <div>
            <label>Academic Year</label>
            <input value={academicYear} onChange={(e) => setAcademicYear(e.target.value)} />
          </div>
          <div>
            <label>Semester</label>
            <select value={semester} onChange={(e) => setSemester(parseInt(e.target.value, 10))}>
              <option value={1}>1</option>
              <option value={2}>2</option>
            </select>
          </div>
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      <h2>Available Courses (Year {profile?.current_year_level})</h2>
      <table>
        <thead><tr><th>Code</th><th>Title</th><th>Credit Hours</th><th>Type</th><th></th></tr></thead>
        <tbody>
          {programmeCourses
            .filter((c) => c.semester_offered === semester)
            .map((c) => (
              <tr key={c.id}>
                <td>{c.code}</td>
                <td>{c.title}</td>
                <td>{c.credit_hours}</td>
                <td>{c.course_type}</td>
                <td>
                  {registeredCourseIds.has(c.id) ? (
                    <span className="badge green">Registered</span>
                  ) : (
                    <button className="btn" disabled={profile?.registration_hold} onClick={() => registerCourse(c.id)}>
                      Register
                    </button>
                  )}
                </td>
              </tr>
            ))}
        </tbody>
      </table>

      <h2>My Registrations This Semester</h2>
      <table>
        <thead><tr><th>Course ID</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {myRegistrations.map((r) => (
            <tr key={r.id}>
              <td>{r.course_id}</td>
              <td>{r.status}</td>
              <td>
                {r.status === 'Registered' && (
                  <button className="btn secondary" onClick={() => dropCourse(r.id)}>Drop</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </PortalLayout>
  )
}
