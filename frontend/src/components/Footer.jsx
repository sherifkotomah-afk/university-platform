import { Link } from 'react-router-dom'
import { Facebook, Instagram, Twitter, Linkedin, Youtube } from 'lucide-react'
import { BRAND } from '../config/brand'

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-grid">
        <div className="footer-brand">
          <h3 style={{ color: 'white', marginBottom: '0.5rem' }}>{BRAND.institutionName}</h3>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem' }}>{BRAND.tagline}</p>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem', marginTop: '1rem' }}>
            {BRAND.address}<br />
            {BRAND.contactPhone}<br />
            {BRAND.contactEmail}
          </p>
        </div>

        <div>
          <h4>Quick Links</h4>
          <ul>
            <li><Link to="/academics">Programmes</Link></li>
            <li><Link to="/admissions">Admissions</Link></li>
            <li><Link to="/login">Student Portal</Link></li>
            <li><Link to="/login">Faculty Portal</Link></li>
          </ul>
        </div>

        <div>
          <h4>University</h4>
          <ul>
            <li><Link to="/academics">About</Link></li>
            <li><Link to="/news">News</Link></li>
            <li><Link to="/news">Events</Link></li>
            <li><Link to="/contact">Contact</Link></li>
          </ul>
        </div>

        <div>
          <h4>Connect With Us</h4>
          <div className="social-icons">
            <a href="#" aria-label="Facebook"><Facebook size={18} /></a>
            <a href="#" aria-label="Instagram"><Instagram size={18} /></a>
            <a href="#" aria-label="Twitter"><Twitter size={18} /></a>
            <a href="#" aria-label="LinkedIn"><Linkedin size={18} /></a>
            <a href="#" aria-label="YouTube"><Youtube size={18} /></a>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} {BRAND.institutionName}. All rights reserved.</p>
      </div>
    </footer>
  )
}
