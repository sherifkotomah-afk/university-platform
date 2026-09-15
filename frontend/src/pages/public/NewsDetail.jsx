import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Navbar from '../../components/Navbar'
import Footer from '../../components/Footer'
import api from '../../api/client'

export default function NewsDetail() {
  const { id } = useParams()
  const [post, setPost] = useState(null)

  useEffect(() => {
    api.get(`/content/news/${id}`).then((res) => setPost(res.data)).catch(() => {})
  }, [id])

  return (
    <div>
      <Navbar />
      <div className="container">
        {!post && <p>Loading...</p>}
        {post && (
          <article className="card">
            <h1>{post.title}</h1>
            <p style={{ whiteSpace: 'pre-wrap' }}>{post.body}</p>
          </article>
        )}
      </div>
      <Footer />
    </div>
  )
}
