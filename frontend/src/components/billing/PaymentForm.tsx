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
    <form
      onSubmit={handleSubmit}
      className="payment-form mt-6"
    >
      <div className="card p-6 md:p-8 max-w-2xl">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-slate-900">Payment</h2>
          <p className="text-sm text-slate-500">
            Complete your booking with secure payment.
          </p>
          <p className="mt-3 text-sm font-semibold text-slate-800">
            Total Amount:{' '}
            <span className="text-lg text-slate-900">
              ${booking.totalPrice.toFixed(2)}
            </span>
          </p>
        </div>

        <div className="space-y-5">
          {/* Payment Method */}
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Payment Method
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setMethod('CREDIT_CARD')}
                className={`w-full rounded-xl border-2 px-4 py-3 text-sm font-semibold transition-all ${
                  method === 'CREDIT_CARD'
                    ? 'border-slate-700 bg-slate-900 text-white shadow-lg shadow-slate-400/30'
                    : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-400 hover:bg-white'
                }`}
              >
                Credit Card
              </button>
              <button
                type="button"
                onClick={() => setMethod('PAYPAL')}
                className={`w-full rounded-xl border-2 px-4 py-3 text-sm font-semibold transition-all ${
                  method === 'PAYPAL'
                    ? 'border-slate-700 bg-slate-900 text-white shadow-lg shadow-slate-400/30'
                    : 'border-slate-200 bg-slate-50 text-slate-700 hover:border-slate-400 hover:bg-white'
                }`}
              >
                PayPal
              </button>
            </div>
          </div>

          {/* Credit Card Fields */}
          {method === 'CREDIT_CARD' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Card Number
                </label>
                <input
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  required
                  className="input-field"
                  placeholder="1234 5678 9012 3456"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Expiry Month
                </label>
                <input
                  value={expiryMonth}
                  onChange={(e) => setExpiryMonth(e.target.value)}
                  required
                  className="input-field"
                  placeholder="MM"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Expiry Year
                </label>
                <input
                  value={expiryYear}
                  onChange={(e) => setExpiryYear(e.target.value)}
                  required
                  className="input-field"
                  placeholder="YYYY"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  CVV
                </label>
                <input
                  value={cvv}
                  onChange={(e) => setCvv(e.target.value)}
                  required
                  className="input-field"
                  placeholder="123"
                />
              </div>
            </div>
          )}

          {/* PayPal Field */}
          {method === 'PAYPAL' && (
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                PayPal Email
              </label>
              <input
                type="email"
                value={paypalEmail}
                onChange={(e) => setPaypalEmail(e.target.value)}
                required
                className="input-field"
                placeholder="you@example.com"
              />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mt-2 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full mt-4 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? 'Processing…' : 'Pay Now'}
          </button>
        </div>
      </div>
    </form>
  );
}
