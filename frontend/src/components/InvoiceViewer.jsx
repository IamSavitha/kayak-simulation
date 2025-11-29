import { useEffect, useState } from 'react';
import { getInvoice } from '../api/billingApi';

export default function InvoiceViewer({ billingId }) {
  const [invoice, setInvoice] = useState(null);

  useEffect(() => {
    if (!billingId) return;
    getInvoice(billingId).then(setInvoice);
  }, [billingId]);

  if (!billingId) return null;
  if (!invoice) return <div>Loading invoice…</div>;

  const { payload } = invoice;
  return (
    <div className="invoice-viewer">
      <h2>Invoice {payload.invoiceNumber}</h2>
      <pre>{JSON.stringify(payload, null, 2)}</pre>
    </div>
  );
}
