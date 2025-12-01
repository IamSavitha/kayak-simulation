// backend/src/server.js
require('dotenv').config();
const app = require('./app');
const connectMongo = require('./config/db.mongo');
const { startBookingConsumer } = require('./services/booking.consumer');
// CHANGED: path now points into backend/kafka
const { startPaymentConsumer } = require('../kafka/paymentConsumer');

async function start() {
  await connectMongo();
  await startBookingConsumer();
  await startPaymentConsumer(); // start payment Kafka consumer

  const port = process.env.PORT || 8005;
  app.listen(port, () => console.log(`Billing service on :${port}`));
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
