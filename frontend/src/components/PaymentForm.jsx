import { useState } from 'react';
import { createBilling } from '../api/billingApi';

export default function PaymentForm({ booking, onPaymentComplete }) {
  const [method, setMethod] = useState('CREDIT_CARD');
  const [cardNumber, setCardNumber] = useState('');
  const [cvv, setCvv] = useState('');
  const [expiryMonth, setExpiryMonth] = useState('');
  const [expiryYear, setExpiryYear] = useState('');
  const [paypalEmail, setPaypalEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payment = {
        method,
        details:
          method === 'CREDIT_CARD'
            ? { cardNumber, cvv, expiryMonth, expiryYear }
            : { paypalEmail }
      };

      const result = await createBilling({
        userId: booking.userId,
        bookingType: booking.type, 
        bookingId: booking.id,
        totalAmount: booking.totalPrice,
        currency: 'USD',
        payment
      });

      onPaymentComplete(result);
    } catch (err) {
      const msg = err.response?.data?.error || 'Payment failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="payment-form">
      <h2>Payment</h2>
      <p>Total Amount: ${booking.totalPrice.toFixed(2)}</p>

      <label>
        Payment Method
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="CREDIT_CARD">Credit Card</option>
          <option value="PAYPAL">PayPal</option>
        </select>
      </label>

      {method === 'CREDIT_CARD' && (
        <>
          <label>
            Card Number
            <input
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value)}
              required
            />
          </label>
          <label>
            Expiry Month
            <input
              value={expiryMonth}
              onChange={(e) => setExpiryMonth(e.target.value)}
              required
            />
          </label>
          <label>
            Expiry Year
            <input
              value={expiryYear}
              onChange={(e) => setExpiryYear(e.target.value)}
              required
            />
          </label>
          <label>
            CVV
            <input
              value={cvv}
              onChange={(e) => setCvv(e.target.value)}
              required
            />
          </label>
        </>
      )}

      {method === 'PAYPAL' && (
        <label>
          PayPal Email
          <input
            type="email"
            value={paypalEmail}
            onChange={(e) => setPaypalEmail(e.target.value)}
            required
          />
        </label>
      )}

      {error && <div className="error">{error}</div>}

      <button disabled={loading}>{loading ? 'Processing…' : 'Pay Now'}</button>
    </form>
  );
}
