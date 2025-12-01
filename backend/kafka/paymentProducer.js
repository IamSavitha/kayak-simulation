// backend/src/services/payment.producer.js
require('dotenv').config();
const { Kafka } = require('kafkajs');

// KAFKA_BROKERS in .env is a comma-separated list like "kafka:9092"
const brokers = (process.env.KAFKA_BROKERS || 'kafka:9092')
  .split(',')
  .map((b) => b.trim())
  .filter(Boolean);

const kafka = new Kafka({
  clientId: 'billing-service-frontend',
  brokers,
});

let producer;

/**
 * Lazily initialize the Kafka producer.
 */
async function getProducer() {
  if (!producer) {
    producer = kafka.producer();
    await producer.connect();
    console.log('[payment.producer] Kafka producer connected');
  }
  return producer;
}

/**
 * Sends a payment request message to the Kafka topic.
 * payload: { bookingEvent: {...}, payment: {...}, requestedAt: ... }
 */
async function sendPaymentRequest(payload) {
  const topic = process.env.PAYMENT_REQUEST_TOPIC || 'billing.payment.requests';
  const p = await getProducer();

  await p.send({
    topic,
    messages: [
      {
        key: String(payload.bookingEvent?.bookingId || 'unknown'),
        value: JSON.stringify(payload),
      },
    ],
  });

  console.log(
    '[payment.producer] Sent payment request for booking',
    payload.bookingEvent?.bookingId
  );
}

module.exports = {
  sendPaymentRequest,
};
