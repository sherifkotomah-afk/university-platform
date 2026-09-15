import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../../components/Navbar'
import Footer from '../../components/Footer'
import api from '../../api/client'

export default function News() {
  const [news, setNews] = useState([])

  useEffect(() => {
    api.get('/content/news').then((res) => setNews(res.data)).catch(() => {})
  }, [])

  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>News & Events</h1>
        {news.length === 0 && <p>No news posted yet.</p>}
        {news.map((post) => (
          <div key={post.id} className="card">
            <h3><Link to={`/news/${post.id}`}>{post.title}</Link></h3>
            <p>{post.body.slice(0, 200)}...</p>
          </div>
        ))}
      </div>
      <Footer />
    </div>
  )
}
