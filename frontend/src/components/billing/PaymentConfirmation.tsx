export interface PaymentResult {
  billing_id?: string;
  booking_id?: string;
  amount?: number;
  payment_status?: string;
  error?: string;
  detail?: string;
  message?: string;
  // fallback legacy fields from old Node API
  status?: string;
  billingId?: string;
  transactionId?: string;
  invoiceNumber?: string;
}

interface PaymentConfirmationProps {
  result: PaymentResult | null;
}

export default function PaymentConfirmation({ result }: PaymentConfirmationProps) {
  if (!result) return null;

  // Prefer new FastAPI-style payment_status, fall back to legacy status field
  const status =
    result.payment_status ||
    result.status ||
    (result.error || result.detail ? 'FAILED' : 'COMPLETED');

  const isSuccess =
    status.toUpperCase() === 'COMPLETED' || status.toUpperCase() === 'SUCCESS';

  const billingId = result.billing_id || result.billingId || 'N/A';
  const bookingId = result.booking_id || 'N/A';
  const amount = typeof result.amount === 'number' ? result.amount : undefined;

  const errorMessage =
    result.error ||
    result.detail ||
    result.message ||
    (!isSuccess ? 'There was an issue processing your payment.' : '');

  return (
    <div className="payment-confirm mt-6">
      <div className="card p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              Payment {status}
            </h2>
            <p className="text-sm text-slate-500">
              {isSuccess
                ? 'Your payment has been processed successfully.'
                : 'There was an issue processing your payment.'}
            </p>
          </div>
          <span
            className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${
              isSuccess
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {status}
          </span>
        </div>

        {isSuccess ? (
          <div className="grid gap-3 text-sm text-slate-800">
            <div className="flex justify-between">
              <span className="font-medium text-slate-600">Billing ID</span>
              <span className="font-semibold">{billingId}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-600">Booking ID</span>
              <span className="font-semibold">{bookingId}</span>
            </div>
            {amount !== undefined && (
              <div className="flex justify-between">
                <span className="font-medium text-slate-600">Amount Paid</span>
                <span className="font-semibold">${amount.toFixed(2)}</span>
              </div>
            )}
          </div>
        ) : (
          <div className="mt-2 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            <p>
              <span className="font-semibold">Error:</span>{' '}
              {errorMessage}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
