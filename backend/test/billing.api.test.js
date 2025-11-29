const request = require('supertest');
const app = require('../src/app');
const db = require('../src/config/db.mysql');

describe('Billing API', () => {
  afterAll(async () => {
    await db.end();
  });

  test('creates billing and processes payment success', async () => {
    jest.spyOn(Math, 'random').mockReturnValue(0.5); 
    const res = await request(app)
      .post('/billing')
      .send({
        userId: '123-45-6789',
        bookingType: 'HOTEL',
        bookingId: 1,
        totalAmount: 100,
        currency: 'USD',
        payment: {
          method: 'CREDIT_CARD',
          details: { cardNumber: '4111111111111111', cvv: '123', expiryMonth: '12', expiryYear: '29' }
        }
      });

    expect(res.status).toBe(201);
    expect(res.body.status).toBe('COMPLETED');
    expect(res.body.billingId).toBeDefined();

    Math.random.mockRestore();
  });

  test('fails on invalid card', async () => {
    const res = await request(app)
      .post('/billing')
      .send({
        userId: '123-45-6789',
        bookingType: 'HOTEL',
        bookingId: 2,
        totalAmount: 100,
        currency: 'USD',
        payment: {
          method: 'CREDIT_CARD',
          details: { cardNumber: '123', cvv: '1' }
        }
      });

    expect(res.status).toBe(402);
    expect(res.body.status).toBe('FAILED');
  });
});
