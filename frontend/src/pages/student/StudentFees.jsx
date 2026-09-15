import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import PortalLayout from '../../components/PortalLayout'
import { STUDENT_LINKS } from './StudentDashboard'
import api from '../../api/client'

export default function StudentFees() {
  const [invoices, setInvoices] = useState([])
  const [payingId, setPayingId] = useState(null)
  const [amount, setAmount] = useState('')
  const [error, setError] = useState('')
  const [verifyStatus, setVerifyStatus] = useState('')
  const [searchParams] = useSearchParams()

  function load() {
    api.get('/fees/invoices/mine').then((res) => setInvoices(res.data)).catch(() => {})
  }

  useEffect(() => { load() }, [])

  // When Paystack redirects back with ?reference=..., verify it server-side.
  useEffect(() => {
    const reference = searchParams.get('reference') || searchParams.get('trxref')
    if (reference) {
      setVerifyStatus('Verifying payment...')
      api.post('/fees/payments/verify', { reference })
        .then((res) => {
          setVerifyStatus(res.data.status === 'Successful' ? 'Payment successful!' : 'Payment could not be confirmed.')
          load()
        })
        .catch(() => setVerifyStatus('Could not verify payment. Contact finance office if you were charged.'))
    }
  }, [searchParams])

  async function handlePay(invoiceId) {
    setError('')
    try {
      const { data } = await api.post('/fees/payments/initiate', { invoice_id: invoiceId, amount: parseFloat(amount) })
      window.location.href = data.authorization_url // redirect to Paystack checkout
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not start payment.')
    }
  }

  return (
    <PortalLayout links={STUDENT_LINKS}>
      <h1>Fees & Payments</h1>
      {verifyStatus && <div className="card">{verifyStatus}</div>}

      {invoices.length === 0 && <p>No invoices yet.</p>}

      {invoices.map((inv) => (
        <div key={inv.id} className="card">
          <h3>{inv.academic_year} — Semester {inv.semester}</h3>
          <table>
            <thead><tr><th>Fee Item</th><th>Amount (GHS)</th></tr></thead>
            <tbody>
              {inv.line_items.map((li) => (
                <tr key={li.id}>
                  <td>{li.fee_item?.name || 'Fee item'} {li.opted_out && '(opted out)'}</td>
                  <td>{li.amount.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p>
            Total: GHS {inv.total_amount.toFixed(2)} · Paid: GHS {inv.amount_paid.toFixed(2)} ·{' '}
            <span className={`badge ${inv.status === 'Paid' ? 'green' : inv.status === 'Partially Paid' ? 'yellow' : 'red'}`}>
              {inv.status}
            </span>
          </p>

          {inv.status !== 'Paid' && (
            payingId === inv.id ? (
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                <input
                  type="number"
                  placeholder="Amount to pay (GHS)"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  style={{ maxWidth: '160px' }}
                />
                <button className="btn" onClick={() => handlePay(inv.id)}>Pay with Paystack</button>
                <button className="btn secondary" onClick={() => setPayingId(null)}>Cancel</button>
              </div>
            ) : (
              <button className="btn" onClick={() => { setPayingId(inv.id); setAmount((inv.total_amount - inv.amount_paid).toFixed(2)) }}>
                Make a Payment
              </button>
            )
          )}
        </div>
      ))}
      {error && <p className="error-text">{error}</p>}
    </PortalLayout>
  )
}
