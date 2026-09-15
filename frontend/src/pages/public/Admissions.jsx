import { Link } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import Navbar from '../../components/Navbar'

export default function Admissions() {
  const { user } = useAuth()

  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>Admissions</h1>
        <div className="card">
          <h2>Entry Requirements</h2>
          <p>
            Applicants are admitted based on WASSCE (or equivalent) results, typically requiring
            passes in English Language, Mathematics, and Integrated Science or Social Studies,
            plus three relevant elective subjects. Foreign WASSCE holders must provide a GTEC
            verification reference.
          </p>
        </div>
        <div className="card">
          <h2>How to Apply</h2>
          <ol>
            <li>Create an applicant account</li>
            <li>Fill in your WASSCE / qualification details</li>
            <li>Upload your supporting documents (result slip, passport photo, transcripts)</li>
            <li>Submit and track your application status online</li>
          </ol>
          {user ? (
            user.role === 'applicant' ? (
              <Link to="/applicant/apply" className="btn">Start Your Application</Link>
            ) : (
              <p>You're logged in as a {user.role}. Applications are only for applicant accounts.</p>
            )
          ) : (
            <Link to="/register" className="btn">Create an Applicant Account</Link>
          )}
        </div>
      </div>
    </div>
  )
}
