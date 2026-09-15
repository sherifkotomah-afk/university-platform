import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../../api/client'
import Navbar from '../../components/Navbar'
import { BRAND } from '../../config/brand'

export default function Home() {
  const [news, setNews] = useState([])

  useEffect(() => {
    api.get('/content/news').then((res) => setNews(res.data.slice(0, 3))).catch(() => {})
  }, [])

  return (
    <div>
      <Navbar />
      <div className="hero">
        <div className="hero-inner">
          <div>
            <h1>{BRAND.tagline}</h1>
            <p>
              {BRAND.institutionName} offers accredited programmes across
              undergraduate and graduate study, built around Ghana's academic
              structure — from application through graduation.
            </p>
            <div className="hero-actions">
              <Link to="/admissions" className="btn">Apply Now</Link>
              <Link to="/academics" className="btn secondary">Explore Programmes</Link>
            </div>
          </div>
          <div className="hero-stats">
            <div className="stat"><span className="label">Faculties &amp; Schools</span><span className="num">6+</span></div>
            <div className="stat"><span className="label">Accredited Programmes</span><span className="num">40+</span></div>
            <div className="stat"><span className="label">Academic Year</span><span className="num">2026/2027</span></div>
          </div>
        </div>
      </div>

      <div className="container">
        <h2 className="section-heading">Latest News</h2>
        <div className="grid cols-3">
          {news.length === 0 && <p>No news posted yet.</p>}
          {news.map((post) => (
            <div key={post.id} className="news-card">
              <h3>{post.title}</h3>
              <p style={{ color: 'var(--color-muted)', fontSize: '0.95rem' }}>{post.body.slice(0, 120)}...</p>
              <Link to={`/news/${post.id}`}>Read more</Link>
            </div>
          ))}
        </div>
      </div>

      <div className="footer">
        <p style={{ margin: '0 auto' }}>{BRAND.institutionName}</p>
        <p style={{ margin: '0.25rem auto 0' }}>{BRAND.address}</p>
        <p style={{ margin: '0.25rem auto 0' }}>{BRAND.contactEmail}</p>
      </div>
    </div>
  )
}
