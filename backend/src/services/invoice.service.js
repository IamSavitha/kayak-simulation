const Invoice = require('../models/invoice.model');

function buildInvoicePayload(billing) {
  return {
    invoiceNumber: `INV-${billing.billing_id}`,
    userId: billing.user_id,
    bookingType: billing.booking_type,
    bookingId: billing.booking_id,
    transactionDate: billing.transaction_date,
    totalAmount: billing.total_amount,
    currency: billing.currency,
    paymentMethod: billing.payment_method,
    transactionStatus: billing.transaction_status
  };
}

async function generateInvoiceForBilling(billing) {
  const payload = buildInvoicePayload(billing);
  const invoice = new Invoice({
    billingId: billing.billing_id,
    invoiceNumber: payload.invoiceNumber,
    payload
  });
  await invoice.save();
  return invoice;
}

async function getInvoiceByBillingId(billingId) {
  return Invoice.findOne({ billingId });
}

module.exports = {
  generateInvoiceForBilling,
  getInvoiceByBillingId
};
