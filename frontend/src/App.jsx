import { useState } from 'react';
import PaymentForm from './components/PaymentForm';
import PaymentConfirmation from './components/PaymentConfirmation';
import BillingHistory from './components/BillingHistory';
import InvoiceViewer from './components/InvoiceViewer';

function App() {
  const [paymentResult, setPaymentResult] = useState(null);
  const [selectedBillingId, setSelectedBillingId] = useState(null);

  const sampleBooking = {
    id: 123,
    type: 'HOTEL',
    userId: '123-45-6789',
    totalPrice: 350.0
  };

  return (
    <div className="app">
      <h1>Kayak Billing & Payments</h1>

      <PaymentForm
        booking={sampleBooking}
        onPaymentComplete={(res) => {
          setPaymentResult(res);
          if (res.billingId) setSelectedBillingId(res.billingId);
        }}
      />

      <PaymentConfirmation result={paymentResult} />

      <BillingHistory
        userId={sampleBooking.userId}
        onSelectBilling={setSelectedBillingId}
      />

      <InvoiceViewer billingId={selectedBillingId} />
    </div>
  );
}

export default App;
