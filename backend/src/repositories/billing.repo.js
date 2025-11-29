const db = require('../config/db.mysql');

async function createBilling(billing) {
  const [result] = await db.execute(
    `INSERT INTO billing
     (user_id, booking_type, booking_id, total_amount, currency,
      payment_method, transaction_status, metadata)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
    [
      billing.userId,
      billing.bookingType,
      billing.bookingId,
      billing.totalAmount,
      billing.currency || 'USD',
      billing.paymentMethod,
      billing.transactionStatus || 'PENDING',
      JSON.stringify(billing.metadata || {})
    ]
  );
  return { ...billing, billingId: result.insertId };
}

async function getBillingById(id) {
  const [rows] = await db.execute(`SELECT * FROM billing WHERE billing_id = ?`, [
    id
  ]);
  return rows[0] || null;
}

async function updateStatus(billingId, status) {
  await db.execute(
    `UPDATE billing SET transaction_status = ? WHERE billing_id = ?`,
    [status, billingId]
  );
}

async function setInvoiceRef(billingId, invoiceRef) {
  await db.execute(
    `UPDATE billing SET invoice_ref = ? WHERE billing_id = ?`,
    [invoiceRef, billingId]
  );
}

async function getBillingByUser(userId) {
  const [rows] = await db.execute(
    `SELECT * FROM billing WHERE user_id = ? ORDER BY transaction_date DESC`,
    [userId]
  );
  return rows;
}

async function getBillingByDate(date) {
  const [rows] = await db.execute(
    `SELECT * FROM billing WHERE DATE(transaction_date) = ?`,
    [date]
  );
  return rows;
}

async function getBillingByMonth(year, month) {
  const [rows] = await db.execute(
    `SELECT * FROM billing
     WHERE YEAR(transaction_date) = ? AND MONTH(transaction_date) = ?`,
    [year, month]
  );
  return rows;
}

async function getRevenueSummary({ year, month }) {
  const [rows] = await db.execute(
    `SELECT booking_type,
            SUM(total_amount) as revenue,
            COUNT(*) as transactions
     FROM billing
     WHERE YEAR(transaction_date) = ? AND MONTH(transaction_date) = ?
       AND transaction_status = 'COMPLETED'
     GROUP BY booking_type`,
    [year, month]
  );
  return rows;
}

module.exports = {
  createBilling,
  getBillingById,
  updateStatus,
  setInvoiceRef,
  getBillingByUser,
  getBillingByDate,
  getBillingByMonth,
  getRevenueSummary
};
