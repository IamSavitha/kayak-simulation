import { FormEvent, useState } from 'react';
import { createPayment } from '../../api/billingApi';

interface Booking {
  id: string | number;
  type: string;
  userId: string;
  totalPrice: number;
}

interface PaymentFormProps {
  booking: Booking;
  onPaymentComplete: (result: any) => void;
}

export default function PaymentForm({ booking, onPaymentComplete }: PaymentFormProps) {
  const [method, setMethod] = useState<'CREDIT_CARD' | 'PAYPAL'>('CREDIT_CARD');
  const [cardNumber, setCardNumber] = useState('');
  const [cardholderName, setCardholderName] = useState('');
  const [cvv, setCvv] = useState('');
  const [expiryMonth, setExpiryMonth] = useState('');
  const [expiryYear, setExpiryYear] = useState('');
  const [paypalEmail, setPaypalEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const paymentMethod = method === 'CREDIT_CARD' ? 'credit_card' : 'paypal';

      const payload: any = {
        booking_id: String(booking.id),
        payment_method: paymentMethod,
      };

      if (paymentMethod === 'credit_card') {
        // Card expiry must be in MM/YY format according to PaymentRequest validator
        const month = expiryMonth.trim();
        const yearTwoDigits = expiryYear.trim().slice(-2); // '2030' -> '30'

        payload.card_number = cardNumber.replace(/\s+/g, '');
        payload.card_expiry = `${month}/${yearTwoDigits}`;
        payload.card_cvv = cvv;
        if (cardholderName.trim()) {
          payload.cardholder_name = cardholderName.trim();
        }
      } else {
        payload.paypal_email = paypalEmail;
      }

      const result = await createPayment(payload);
      onPaymentComplete(result);
    } catch (err: any) {
      let msg = 'Payment failed';
      const data = err?.response?.data;

      if (data) {
        if (typeof data === 'string') {
          msg = data;
        } else if (data.detail) {
          const detail = data.detail;
          if (Array.isArray(detail) && detail.length > 0) {
            // FastAPI / Pydantic validation errors
            msg = detail
              .map((d: any) => d.msg || JSON.stringify(d))
              .join('; ');
          } else if (typeof detail === 'string') {
            msg = detail;
          } else {
            msg = JSON.stringify(detail);
          }
        } else if (data.error || data.message) {
          msg = data.error || data.message;
        }
      }

      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="payment-form mt-6">
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
                  required={method === 'CREDIT_CARD'}
                  className="input-field"
                  placeholder="4111 1111 1111 1111"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Cardholder Name
                </label>
                <input
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)}
                  required={method === 'CREDIT_CARD'}
                  className="input-field"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Expiry Month
                </label>
                <input
                  value={expiryMonth}
                  onChange={(e) => setExpiryMonth(e.target.value)}
                  required={method === 'CREDIT_CARD'}
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
                  required={method === 'CREDIT_CARD'}
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
                  required={method === 'CREDIT_CARD'}
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
                required={method === 'PAYPAL'}
                className="input-field"
                placeholder="test.paypal@example.com"
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
