const express = require('express');
const billingRepo = require('../repositories/billing.repo');
const { getBillingWithCache } = require('../services/billing.service');
const {
  getRevenueSummaryByMonth,
  getRevenueByProperty,
  getRevenueByCity,
  getRevenueByProvider
} = require("../repositories/billing.repo");
const router = express.Router();

function requireAdmin(req, res, next) {
  if (req.headers['x-admin'] !== 'true') {
    return res.status(403).json({ error: 'Admin only' });
  }
  next();
}

router.use(requireAdmin);

router.get('/by-date', async (req, res) => {
  const { date } = req.query;
  const rows = await billingRepo.getBillingByDate(date);
  res.json(rows);
});

router.get('/by-month', async (req, res) => {
  const { year, month } = req.query;
  const rows = await billingRepo.getBillingByMonth(year, month);
  res.json(rows);
});

router.get('/by-user', async (req, res) => {
  const { userId } = req.query;
  const rows = await billingRepo.getBillingByUser(userId);
  res.json(rows);
});

router.get('/:billingId', async (req, res) => {
  const billing = await getBillingWithCache(req.params.billingId);
  if (!billing) return res.status(404).json({ error: 'Not found' });
  res.json(billing);
});

router.put('/:billingId/status', async (req, res) => {
  const { status } = req.body;
  await billingRepo.updateStatus(req.params.billingId, status);
  const updated = await getBillingWithCache(req.params.billingId);
  res.json(updated);
});

router.get('/revenue-summary', async (req, res) => {
  const { year, month } = req.query;
  const rows = await billingRepo.getRevenueSummary({ year, month });
  res.json(rows);
});

router.get("/billing/revenue-by-property", async (req, res) => {
  try {
    const year = Number(req.query.year);
    if (!year) {
      return res.status(400).json({ error: "year is required and must be a number" });
    }

    const result = await getRevenueByProperty(year);
    return res.json(result);
  } catch (err) {
    console.error("revenue-by-property error", err);
    return res.status(500).json({ error: "Internal server error" });
  }
});

router.get("/billing/revenue-by-city", async (req, res) => {
  try {
    const year = Number(req.query.year);
    if (!year) {
      return res.status(400).json({ error: "year is required and must be a number" });
    }

    const result = await getRevenueByCity(year);
    return res.json(result);
  } catch (err) {
    console.error("revenue-by-city error", err);
    return res.status(500).json({ error: "Internal server error" });
  }
});

router.get("/billing/revenue-by-provider", async (req, res) => {
  try {
    const year = Number(req.query.year);
    const month = Number(req.query.month);

    if (!year || !month) {
      return res.status(400).json({
        error: "year and month are required and must be numbers"
      });
    }

    const result = await getRevenueByProvider(year, month);
    return res.json(result);
  } catch (err) {
    console.error("revenue-by-provider error", err);
    return res.status(500).json({ error: "Internal server error" });
  }
});

module.exports = router;

