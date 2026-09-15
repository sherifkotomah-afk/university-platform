import Navbar from '../../components/Navbar'
import { BRAND } from '../../config/brand'

export default function Contact() {
  return (
    <div>
      <Navbar />
      <div className="container">
        <h1>Contact Us</h1>
        <div className="card">
          <p><strong>Email:</strong> {BRAND.contactEmail}</p>
          <p><strong>Phone:</strong> {BRAND.contactPhone}</p>
          <p><strong>Address:</strong> {BRAND.address}</p>
        </div>
      </div>
    </div>
  )
}
