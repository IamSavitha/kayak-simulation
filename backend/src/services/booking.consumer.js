// backend/kafka/paymentConsumer.js
require('dotenv').config();
const { Kafka } = require('kafkajs');
const { createBillingFromBooking } = require('../src/services/billing.service');

// KAFKA_BROKERS env is a comma-separated list, e.g. "kafka:9092"
const brokers = (process.env.KAFKA_BROKERS || 'kafka:9092')
  .split(',')
  .map((b) => b.trim())
  .filter(Boolean);

const kafka = new Kafka({
  clientId: 'billing-service-backend',
  brokers,
});

const consumer = kafka.consumer({
  groupId: process.env.KAFKA_BILLING_GROUP || 'billing-payments-consumer',
});

const producer = kafka.producer();

/**
 * Start the payment Kafka consumer.
 * Listens for payment requests and calls createBillingFromBooking,
 * then emits a payment result event.
 */
async function startPaymentConsumer() {
  const requestTopic = process.env.PAYMENT_REQUEST_TOPIC || 'billing.payment.requests';
  const resultTopic = process.env.PAYMENT_RESULT_TOPIC || 'billing.payment.results';

  await consumer.connect();
  await producer.connect();

  await consumer.subscribe({ topic: requestTopic, fromBeginning: false });
  console.log('[paymentConsumer] Subscribed to', requestTopic);

  await consumer.run({
    eachMessage: async ({ topic, message }) => {
      try {
        const payloadStr = message.value.toString();
        const payload = JSON.parse(payloadStr);

        console.log('[paymentConsumer] Received payment request', payload);

        const { bookingEvent, payment, requestedAt } = payload;

        // Reuse your existing billing creation logic
        const result = await createBillingFromBooking({ bookingEvent, payment });

        const resultPayload = {
          bookingEvent,
          payment,
          requestedAt,
          processedAt: new Date().toISOString(),
          ...result, // e.g. { status: 'SUCCESS', billingId: ..., ... }
        };

        await producer.send({
          topic: resultTopic,
          messages: [
            {
              key: String(bookingEvent?.bookingId || 'unknown'),
              value: JSON.stringify(resultPayload),
            },
          ],
        });

        console.log(
          '[paymentConsumer] Published payment result for booking',
          bookingEvent?.bookingId,
          'status =',
          result.status
        );
      } catch (err) {
        console.error('[paymentConsumer] Error handling payment message', err);
      }
    },
  });
}

// Allow running this file directly: `node backend/kafka/paymentConsumer.js`
if (require.main === module) {
  startPaymentConsumer()
    .then(() => console.log('[paymentConsumer] started'))
    .catch((err) => {
      console.error('[paymentConsumer] failed to start', err);
      process.exit(1);
    });
}

module.exports = {
  startPaymentConsumer,
};
