import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

const LINKS = [
  { to: '/applicant/dashboard', label: 'Dashboard' },
  { to: '/applicant/apply', label: 'Apply' },
]

export default function ApplicationForm() {
  const navigate = useNavigate()
  const [programmes, setProgrammes] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    programme_id: '',
    application_type: 'Fresh',
    wassce_index_number: '',
    wassce_year: '',
    core_english_grade: '',
    core_maths_grade: '',
    core_science_or_social_studies_grade: '',
    elective_subjects: [{ subject: '', grade: '' }, { subject: '', grade: '' }, { subject: '', grade: '' }],
    gtec_verification_reference: '',
  })

  useEffect(() => {
    api.get('/academics/programmes').then((res) => setProgrammes(res.data)).catch(() => {})
  }, [])

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }))
  }

  function updateElective(index, field, value) {
    setForm((f) => {
      const electives = [...f.elective_subjects]
      electives[index] = { ...electives[index], [field]: value }
      return { ...f, elective_subjects: electives }
    })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const payload = {
        ...form,
        programme_id: parseInt(form.programme_id, 10),
        wassce_year: form.wassce_year ? parseInt(form.wassce_year, 10) : null,
        elective_subjects: form.elective_subjects.filter((e) => e.subject && e.grade),
      }
      const { data } = await api.post('/applications', payload)
      navigate(`/applicant/applications/${data.id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not submit application.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PortalLayout links={LINKS}>
      <h1>Application Form</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: '600px' }}>
        <div>
          <label>Programme</label>
          <select value={form.programme_id} onChange={(e) => update('programme_id', e.target.value)} required>
            <option value="">Select a programme</option>
            {programmes.map((p) => (
              <option key={p.id} value={p.id}>{p.name} ({p.level})</option>
            ))}
          </select>
        </div>

        <div>
          <label>Application Type</label>
          <select value={form.application_type} onChange={(e) => update('application_type', e.target.value)}>
            <option value="Fresh">Fresh</option>
            <option value="Transfer">Transfer</option>
            <option value="International">International</option>
            <option value="Graduate">Graduate</option>
          </select>
        </div>

        <h3>WASSCE Details</h3>
        <div>
          <label>WASSCE Index Number</label>
          <input value={form.wassce_index_number} onChange={(e) => update('wassce_index_number', e.target.value)} />
        </div>
        <div>
          <label>WASSCE Year</label>
          <input type="number" value={form.wassce_year} onChange={(e) => update('wassce_year', e.target.value)} />
        </div>
        <div>
          <label>Core English Grade</label>
          <input value={form.core_english_grade} onChange={(e) => update('core_english_grade', e.target.value)} placeholder="e.g. A1" />
        </div>
        <div>
          <label>Core Maths Grade</label>
          <input value={form.core_maths_grade} onChange={(e) => update('core_maths_grade', e.target.value)} placeholder="e.g. B2" />
        </div>
        <div>
          <label>Core Science/Social Studies Grade</label>
          <input value={form.core_science_or_social_studies_grade} onChange={(e) => update('core_science_or_social_studies_grade', e.target.value)} />
        </div>

        <h3>Elective Subjects (minimum 3)</h3>
        {form.elective_subjects.map((e, i) => (
          <div key={i} style={{ display: 'flex', gap: '0.5rem' }}>
            <input placeholder="Subject" value={e.subject} onChange={(ev) => updateElective(i, 'subject', ev.target.value)} />
            <input placeholder="Grade" value={e.grade} onChange={(ev) => updateElective(i, 'grade', ev.target.value)} style={{ maxWidth: '80px' }} />
          </div>
        ))}

        <div>
          <label>GTEC Verification Reference (foreign WASSCE only)</label>
          <input value={form.gtec_verification_reference} onChange={(e) => update('gtec_verification_reference', e.target.value)} />
        </div>

        {error && <p className="error-text">{error}</p>}
        <button className="btn" type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Application'}
        </button>
      </form>
    </PortalLayout>
  )
}
