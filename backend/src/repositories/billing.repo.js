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




async function getRevenueByProperty(year) {
  const [rows] = await db.execute(
    `
    SELECT
      l.listing_id,
      l.listing_name,
      l.listing_type,
      SUM(b.total_amount) AS total_revenue,
      COUNT(*) AS booking_count
    FROM billing b
    JOIN listings l
      ON l.listing_id = b.booking_id
      AND l.listing_type = b.booking_type
    WHERE YEAR(b.transaction_date) = ?
      AND b.transaction_status = 'COMPLETED'
    GROUP BY
      l.listing_id,
      l.listing_name,
      l.listing_type
    ORDER BY total_revenue DESC
    LIMIT 10
    `,
    [year]
  );

  const totalRevenue = rows.reduce(
    (sum, r) => sum + Number(r.total_revenue || 0),
    0
  );

  return {
    year: Number(year),
    total_revenue: totalRevenue.toFixed(2),
    items: rows
  };
}

async function getRevenueByCity(year) {
  const [rows] = await db.execute(
    `
    SELECT
      l.city,
      l.state,
      SUM(b.total_amount) AS total_revenue,
      COUNT(*) AS booking_count
    FROM billing b
    JOIN listings l
      ON l.listing_id = b.booking_id
      AND l.listing_type = b.booking_type
    WHERE YEAR(b.transaction_date) = ?
      AND b.transaction_status = 'COMPLETED'
    GROUP BY
      l.city,
      l.state
    ORDER BY total_revenue DESC
    `,
    [year]
  );

  const totalRevenue = rows.reduce(
    (sum, r) => sum + Number(r.total_revenue || 0),
    0
  );

  return {
    year: Number(year),
    total_revenue: totalRevenue.toFixed(2),
    cities: rows
  };
}

async function getRevenueByProvider(year, month) {
  const [rows] = await db.execute(
    `
    SELECT
      p.provider_id,
      p.provider_name,
      COUNT(DISTINCT l.listing_id) AS properties_sold,
      SUM(b.total_amount) AS total_revenue
    FROM billing b
    JOIN listings l
      ON l.listing_id = b.booking_id
      AND l.listing_type = b.booking_type
    JOIN providers p
      ON p.provider_id = l.provider_id
    WHERE YEAR(b.transaction_date) = ?
      AND MONTH(b.transaction_date) = ?
      AND b.transaction_status = 'COMPLETED'
    GROUP BY
      p.provider_id,
      p.provider_name
    ORDER BY total_revenue DESC
    LIMIT 10
    `,
    [year, month]
  );

  const totalRevenue = rows.reduce(
    (sum, r) => sum + Number(r.total_revenue || 0),
    0
  );

  return {
    year: Number(year),
    month: Number(month),
    total_revenue: totalRevenue.toFixed(2),
    providers: rows
  };
}

module.exports = {
  createBilling,
  getBillingById,
  updateStatus,
  setInvoiceRef,
  getBillingByUser,
  getBillingByDate,
  getBillingByMonth,
  getRevenueSummary,
  getRevenueByProperty,
  getRevenueByCity,
  getRevenueByProvider
};