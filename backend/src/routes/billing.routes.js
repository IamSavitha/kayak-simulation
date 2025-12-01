// backend/src/routes/billing.routes.js
const express = require('express');
const billingRepo = require('../repositories/billing.repo');
const invoiceService = require('../services/invoice.service');
const { createBillingFromBooking, getBillingWithCache } = require('../services/billing.service');
// CHANGED: path now points into backend/kafka
const { sendPaymentRequest } = require('../../kafka/paymentProducer');

const router = express.Router();

// Existing synchronous billing creation endpoint (unchanged)
router.post('/', async (req, res) => {
  try {
    const { userId, bookingType, bookingId, totalAmount, currency, payment } = req.body;
    if (!userId || !bookingType || !bookingId || !totalAmount || !payment?.method) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const result = await createBillingFromBooking({
      bookingEvent: { userId, bookingType, bookingId, totalAmount, currency },
      payment
    });

    if (result.status === 'FAILED') {
      return res.status(402).json(result); 
    }

    res.status(201).json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// NEW async payment endpoint -> pushes to Kafka
router.post('/payment', async (req, res) => {
  try {
    const { userId, bookingType, bookingId, totalAmount, currency, payment } = req.body;

    if (!userId || !bookingType || !bookingId || !totalAmount || !payment?.method) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    const payload = {
      bookingEvent: { userId, bookingType, bookingId, totalAmount, currency },
      payment,
      requestedAt: new Date().toISOString()
    };

    await sendPaymentRequest(payload);

    return res.status(202).json({
      status: 'PENDING',
      message: 'Payment request accepted and will be processed asynchronously.'
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Existing routes (kept as-is)
router.get('/:billingId', async (req, res) => {
  const billing = await getBillingWithCache(req.params.billingId);
  if (!billing) return res.status(404).json({ error: 'Not found' });
  res.json(billing);
});

router.get('/user/:userId', async (req, res) => {
  const rows = await billingRepo.getBillingByUser(req.params.userId);
  res.json(rows);
});

router.get('/:billingId/invoice', async (req, res) => {
  const billingId = Number(req.params.billingId);
  const invoice = await invoiceService.getInvoiceByBillingId(billingId);
  if (!invoice) return res.status(404).json({ error: 'Invoice not found' });
  res.json(invoice);
});

module.exports = router;
