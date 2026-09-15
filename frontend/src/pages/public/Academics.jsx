import { useEffect, useState } from 'react'
import Navbar from '../../components/Navbar'
import Footer from '../../components/Footer'
import api from '../../api/client'

export default function Academics() {
  const [schools, setSchools] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/academics/schools')
      .then((res) => setSchools(res.data))
      .catch(() => setError('Could not load academic programmes right now.'))
  }, [])

  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>Academics</h1>
        {error && <p className="error-text">{error}</p>}
        {schools.length === 0 && !error && <p>No programmes published yet.</p>}
        {schools.map((school) => (
          <div key={school.id} className="card">
            <h2>{school.name}</h2>
            {school.departments.map((dept) => (
              <div key={dept.id} style={{ marginLeft: '1rem', marginBottom: '1rem' }}>
                <h3>{dept.name}</h3>
                {dept.programmes.map((prog) => (
                  <div key={prog.id} style={{ marginLeft: '1rem', marginBottom: '0.75rem' }}>
                    <strong>{prog.name}</strong> — {prog.level}, {prog.duration_years} years, {prog.total_credit_hours} credit hours
                    <p style={{ color: '#666', fontSize: '0.9rem' }}>{prog.description}</p>
                    <details>
                      <summary>{prog.courses.length} courses</summary>
                      <ul>
                        {prog.courses.map((c) => (
                          <li key={c.id}>{c.code} — {c.title} ({c.credit_hours} credit hours, {c.course_type})</li>
                        ))}
                      </ul>
                    </details>
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
      <Footer />
    </div>
  )
}
