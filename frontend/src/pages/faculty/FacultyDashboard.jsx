import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

export const FACULTY_LINKS = [
  { to: '/faculty/dashboard', label: 'My Courses' },
]

export default function FacultyDashboard() {
  const [courses, setCourses] = useState([])

  useEffect(() => {
    api.get('/faculty/me/courses').then((res) => setCourses(res.data)).catch(() => {})
  }, [])

  return (
    <PortalLayout links={FACULTY_LINKS}>
      <h1>My Courses</h1>
      <div className="grid cols-3">
        {courses.map((c) => (
          <div key={c.id} className="card">
            <h3>Course #{c.course_id}</h3>
            <p>{c.academic_year} — Semester {c.semester}</p>
            <Link to={`/faculty/courses/${c.id}`} className="btn">Manage</Link>
          </div>
        ))}
        {courses.length === 0 && <p>No courses assigned yet.</p>}
      </div>
    </PortalLayout>
  )
}
