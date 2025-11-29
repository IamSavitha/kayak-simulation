export default function PaymentConfirmation({ result }) {
  if (!result) return null;

  const isSuccess = result.status === 'COMPLETED';

  return (
    <div className="payment-confirm mt-6">
      <div className="card p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              Payment {result.status}
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
            {result.status}
          </span>
        </div>

        {isSuccess ? (
          <div className="grid gap-3 text-sm text-slate-800">
            <div className="flex justify-between">
              <span className="font-medium text-slate-600">Billing ID</span>
              <span className="font-semibold">{result.billingId}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-600">Transaction ID</span>
              <span className="font-semibold">{result.transactionId}</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium text-slate-600">Invoice Number</span>
              <span className="font-semibold">{result.invoiceNumber}</span>
            </div>
          </div>
        ) : (
          <div className="mt-2 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
            <p>
              <span className="font-semibold">Error:</span>{' '}
              {result.error}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
