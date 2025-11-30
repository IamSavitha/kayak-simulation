import { useState } from 'react';
import PaymentForm from '../../components/billing/PaymentForm';
import PaymentConfirmation from '../../components/billing/PaymentConfirmation';
import BillingHistory from '../../components/billing/BillingHistory';
import InvoiceViewer from '../../components/billing/InvoiceViewer';

const BillingPage: React.FC = () => {
  const [paymentResult, setPaymentResult] = useState<any | null>(null);
  const [selectedBillingId, setSelectedBillingId] = useState<string | null>(null);

  // TODO: replace this with real booking from /bookings page later
  const sampleBooking = {
    id: 'BK-123',
    type: 'HOTEL',
    userId: '123-45-6789',
    totalPrice: 350.0,
  };

  const currentUserId = sampleBooking.userId; // later pull from auth / profile

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Billing & Payments</h1>
      <p className="text-slate-600 mb-6">
        Manage your payments, view billing history, and access invoices.
      </p>

      <PaymentForm
        booking={sampleBooking}
        onPaymentComplete={(res: any) => {
          setPaymentResult(res);
          if (res.billing_id) setSelectedBillingId(res.billing_id);
        }}
      />

      <PaymentConfirmation result={paymentResult} />

      <BillingHistory
        userId={currentUserId}
        onSelectBilling={(billingId: string) => setSelectedBillingId(billingId)}
      />

      <InvoiceViewer billingId={selectedBillingId} />
    </div>
  );
};

export default BillingPage;
