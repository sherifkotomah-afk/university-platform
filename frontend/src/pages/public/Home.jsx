import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  GraduationCap, BookOpen, Award, FileText, ArrowRight,
  Landmark, Users, Building2, CalendarClock,
} from 'lucide-react'
import api from '../../api/client'
import Navbar from '../../components/Navbar'
import Footer from '../../components/Footer'
import { BRAND } from '../../config/brand'

const PROGRAMME_LEVELS = [
  { level: 'Undergraduate', icon: GraduationCap, blurb: "Comprehensive degree programmes preparing you for a successful career." },
  { level: 'Masters', icon: BookOpen, blurb: 'Taught and research master\u2019s programmes across diverse disciplines.' },
  { level: 'PhD', icon: Award, blurb: 'Advanced research programmes leading to doctoral qualification.' },
  { level: 'Certificate', icon: FileText, blurb: 'Postgraduate certificates and diplomas for professional development.' },
]

export default function Home() {
  const [news, setNews] = useState([])
  const [programmeCounts, setProgrammeCounts] = useState({})

  useEffect(() => {
    api.get('/content/news').then((res) => setNews(res.data.slice(0, 3))).catch(() => {})

    PROGRAMME_LEVELS.forEach(({ level }) => {
      api.get('/academics/programmes', { params: { level } })
        .then((res) => setProgrammeCounts((prev) => ({ ...prev, [level]: res.data.length })))
        .catch(() => {})
    })
  }, [])

  return (
    <div>
      <Navbar />

      <div className="hero">
        <div className="hero-pattern" aria-hidden="true" />
        <div className="hero-inner">
          <div>
            <p className="hero-eyebrow">{BRAND.shortCode} &middot; Ghana</p>
            <h1>{BRAND.tagline}</h1>
            <p>
              {BRAND.institutionName} offers accredited programmes across
              undergraduate and graduate study, built around Ghana's academic
              structure &mdash; from application through graduation.
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

      <div className="quicklinks-bar">
        <div className="quicklinks-inner">
          <Link to="/login"><Landmark size={16} /> Student Portal</Link>
          <Link to="/login"><Users size={16} /> Faculty Portal</Link>
          <Link to="/academics"><BookOpen size={16} /> Programmes</Link>
          <Link to="/admissions"><FileText size={16} /> Apply</Link>
          <Link to="/academics"><CalendarClock size={16} /> Academic Calendar</Link>
        </div>
      </div>

      <div className="container">
        <h2 className="section-heading">Explore Our Programmes</h2>
        <p style={{ color: 'var(--color-muted)', marginTop: '-0.75rem', marginBottom: '1.75rem' }}>
          Undergraduate, postgraduate, and doctoral study &mdash; designed around Ghana's credit-hour system.
        </p>
        <div className="grid cols-4">
          {PROGRAMME_LEVELS.map(({ level, icon: Icon, blurb }) => (
            <div key={level} className="programme-card">
              <Icon size={28} color="var(--color-accent)" />
              <p className="programme-count">{programmeCounts[level] ?? '\u2013'} programmes</p>
              <h3>{level}</h3>
              <p style={{ fontSize: '0.9rem', color: 'var(--color-muted)' }}>{blurb}</p>
              <Link to="/academics" className="programme-link">Explore <ArrowRight size={14} /></Link>
            </div>
          ))}
        </div>
      </div>

      <div className="stats-band">
        <div className="container stats-band-inner">
          <div className="stat-block">
            <Building2 size={26} />
            <div className="value">6</div>
            <div className="label">Faculties &amp; Schools</div>
          </div>
          <div className="stat-block">
            <GraduationCap size={26} />
            <div className="value">40+</div>
            <div className="label">Accredited Programmes</div>
          </div>
          <div className="stat-block">
            <Users size={26} />
            <div className="value">200+</div>
            <div className="label">Academic Staff</div>
          </div>
          <div className="stat-block">
            <Award size={26} />
            <div className="value">GTEC</div>
            <div className="label">Accredited Institution</div>
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
              <Link to={`/news/${post.id}`}>Read more <ArrowRight size={14} style={{ verticalAlign: 'middle' }} /></Link>
            </div>
          ))}
        </div>
      </div>

      <div className="cta-banner">
        <div className="container">
          <h2 style={{ color: 'white' }}>Ready to Join the {BRAND.shortCode} Community?</h2>
          <p style={{ color: 'rgba(255,255,255,0.85)' }}>
            Apply now to become part of a vibrant academic community and start your journey.
          </p>
          <div className="hero-actions" style={{ justifyContent: 'center' }}>
            <Link to="/admissions" className="btn">Apply Now</Link>
            <Link to="/academics" className="btn secondary">Learn More</Link>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
