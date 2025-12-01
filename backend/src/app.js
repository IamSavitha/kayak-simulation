// backend/src/app.js
const express = require('express');
const cors = require('cors');

const billingRoutes = require('./routes/billing.routes');
const adminRoutes = require('./routes/admin.routes');

const app = express();
app.use(cors());
app.use(express.json());

app.use('/billing', billingRoutes);
app.use('/admin/billing', adminRoutes);

app.get('/health', (_, res) => res.json({ status: 'ok' }));

module.exports = app;
