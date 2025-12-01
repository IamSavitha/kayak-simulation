import { useEffect, useState } from 'react';
import { getInvoice } from '../../api/billingApi';

interface InvoiceViewerProps {
  billingId: string | null;
}

export default function InvoiceViewer({ billingId }: InvoiceViewerProps) {
  const [invoice, setInvoice] = useState<any | null>(null);

  useEffect(() => {
    if (!billingId) return;
    setInvoice(null);
    getInvoice(billingId).then(setInvoice);
  }, [billingId]);

  if (!billingId) return null;

  if (!invoice) {
    return (
      <div className="mt-6">
        <div className="card p-6 md:p-8">
          <p className="text-sm text-slate-600">Loading invoice…</p>
        </div>
      </div>
    );
  }

  // FastAPI billing service returns the invoice payload directly (no { payload: ... } wrapper)
  const payload = invoice;

  return (
    <div className="invoice-viewer mt-6">
      <div className="card p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              Invoice #{payload.invoice_number || payload.invoiceNumber || billingId}
            </h2>
            <p className="text-sm text-slate-500">
              Detailed invoice data for this billing record.
            </p>
          </div>
          <span className="inline-flex items-center rounded-full bg-slate-100 text-xs font-medium text-slate-700 px-3 py-1">
            JSON payload
          </span>
        </div>

        <div className="rounded-2xl bg-slate-900 text-slate-50 text-xs p-4 md:p-5 overflow-x-auto shadow-inner-lg">
          <pre className="whitespace-pre-wrap break-words font-mono">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
