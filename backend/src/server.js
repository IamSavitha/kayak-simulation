// backend/src/server.js
require('dotenv').config();
const app = require('./app');
const connectMongo = require('./config/db.mongo');
const { startBookingConsumer } = require('./services/booking.consumer');
// NEW: payment consumer
const { startPaymentConsumer } = require('./services/payment.consumer');

async function start() {
  await connectMongo();
  await startBookingConsumer();
  // NEW: start Kafka payment consumer
  await startPaymentConsumer();

  const port = process.env.PORT || 8005;
  app.listen(port, () => console.log(`Billing service on :${port}`));
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
