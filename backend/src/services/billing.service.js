const billingRepo = require('../repositories/billing.repo');
const invoiceService = require('./invoice.service');
const paymentService = require('./payment.service');
const redis = require('../config/redis');

const BILLING_CACHE_PREFIX = 'billing:';

async function createBillingFromBooking({ bookingEvent, payment }) {
  //bookingEvent: { userId, bookingType, bookingId, totalAmount, currency }
  const billing = await billingRepo.createBilling({
    userId: bookingEvent.userId,
    bookingType: bookingEvent.bookingType,
    bookingId: bookingEvent.bookingId,
    totalAmount: bookingEvent.totalAmount,
    currency: bookingEvent.currency || 'USD',
    paymentMethod: payment.method,
    transactionStatus: 'PENDING',
    metadata: { bookingEvent }
  });

  const result = await paymentService.processPayment({
    amount: billing.totalAmount,
    method: payment.method,
    details: payment.details
  });

  if (!result.success) {
    await billingRepo.updateStatus(billing.billingId, 'FAILED');
    await redis.del(`${BILLING_CACHE_PREFIX}${billing.billingId}`);
    return { billingId: billing.billingId, status: 'FAILED', error: result.error };
  }

  await billingRepo.updateStatus(billing.billingId, 'COMPLETED');
  const updated = await billingRepo.getBillingById(billing.billingId);

  const invoice = await invoiceService.generateInvoiceForBilling(updated);
  await billingRepo.setInvoiceRef(billing.billingId, invoice.invoiceNumber);

  await redis.set(
    `${BILLING_CACHE_PREFIX}${billing.billingId}`,
    JSON.stringify({ ...updated, invoiceNumber: invoice.invoiceNumber }),
    'EX',
    60 * 5
  );

  return {
    billingId: billing.billingId,
    status: 'COMPLETED',
    transactionId: result.transactionId,
    invoiceNumber: invoice.invoiceNumber
  };
}

async function getBillingWithCache(billingId) {
  const key = `${BILLING_CACHE_PREFIX}${billingId}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const billing = await billingRepo.getBillingById(billingId);
  if (!billing) return null;

  await redis.set(key, JSON.stringify(billing), 'EX', 60 * 5);
  return billing;
}

module.exports = {
  createBillingFromBooking,
  getBillingWithCache
};
