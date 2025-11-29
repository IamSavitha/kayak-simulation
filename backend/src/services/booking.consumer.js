const kafka = require('../config/kafka');
const { createBillingFromBooking } = require('./billing.service');

async function startBookingConsumer() {
  const consumer = kafka.consumer({ groupId: 'billing-consumers' });

  await consumer.connect();
  await consumer.subscribe({ topic: 'booking_created', fromBeginning: false });

  await consumer.run({
    eachMessage: async ({ message }) => {
      try {
        const payload = JSON.parse(message.value.toString());
        console.log('Received booking_created', payload);
        await createBillingFromBooking({
          bookingEvent: payload,
          payment: payload.payment
        });
      } catch (err) {
        console.error('Error processing booking_created', err);
      }
    }
  });
}

module.exports = { startBookingConsumer };
