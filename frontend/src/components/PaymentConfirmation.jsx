export default function PaymentConfirmation({ result }) {
  if (!result) return null;
  return (
    <div className="payment-confirm">
      <h2>Payment {result.status}</h2>
      {result.status === 'COMPLETED' ? (
        <>
          <p>Billing ID: {result.billingId}</p>
          <p>Transaction ID: {result.transactionId}</p>
          <p>Invoice Number: {result.invoiceNumber}</p>
        </>
      ) : (
        <p>Error: {result.error}</p>
      )}
    </div>
  );
}
