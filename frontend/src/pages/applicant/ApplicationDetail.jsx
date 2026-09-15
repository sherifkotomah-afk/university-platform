import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import api from '../../api/client'

const LINKS = [
  { to: '/applicant/dashboard', label: 'Dashboard' },
  { to: '/applicant/apply', label: 'Apply' },
]

const DOC_TYPES = ['WASSCE Result Slip', 'Passport Photo', 'Transcript', 'Recommendation Letter', 'Birth Certificate']

export default function ApplicationDetail() {
  const { id } = useParams()
  const [application, setApplication] = useState(null)
  const [documents, setDocuments] = useState([])
  const [docType, setDocType] = useState(DOC_TYPES[0])
  const [selectedFile, setSelectedFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  function load() {
    api.get(`/applications/${id}`).then((res) => setApplication(res.data))
    api.get(`/applications/${id}/documents`).then((res) => setDocuments(res.data))
  }

  useEffect(() => { load() }, [id])

  async function handleUpload(e) {
    e.preventDefault()
    setError('')
    if (!selectedFile) {
      setError('Choose a file first.')
      return
    }
    setUploading(true)
    try {
      // Step 1: actually upload the file itself to the server.
      const formData = new FormData()
      formData.append('file', selectedFile)
      const uploadRes = await api.post('/uploads/file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      // Step 2: record the document against this application using the
      // URL the upload just returned.
      await api.post(`/applications/${id}/documents`, {
        document_type: docType,
        file_url: uploadRes.data.file_url,
      })
      setSelectedFile(null)
      load()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  if (!application) return <PortalLayout links={LINKS}><p>Loading...</p></PortalLayout>

  return (
    <PortalLayout links={LINKS}>
      <h1>Application #{application.id}</h1>
      <div className="card">
        <p>Status: <span className="badge yellow">{application.status}</span></p>
        <p>Type: {application.application_type}</p>
      </div>

      <h2>Documents</h2>
      <div className="card">
        <ul>
          {documents.map((d) => (
            <li key={d.id}>
              {d.document_type} — {d.verified ? 'Verified' : 'Pending verification'}
              {' '}(<a href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}${d.file_url}`} target="_blank" rel="noreferrer">view</a>)
            </li>
          ))}
          {documents.length === 0 && <li>No documents uploaded yet.</li>}
        </ul>
        <form onSubmit={handleUpload} style={{ marginTop: '1rem' }}>
          <div>
            <label>Document Type</label>
            <select value={docType} onChange={(e) => setDocType(e.target.value)}>
              {DOC_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label>Choose File (PDF, JPG, PNG, DOC — max 10MB)</label>
            <input type="file" accept=".pdf,.jpg,.jpeg,.png,.doc,.docx" onChange={(e) => setSelectedFile(e.target.files[0])} required />
          </div>
          {error && <p className="error-text">{error}</p>}
          <button className="btn" type="submit" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>
    </PortalLayout>
  )
}
