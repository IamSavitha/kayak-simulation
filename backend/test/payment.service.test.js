const { processPayment } = require('../src/services/payment.service');

describe('Payment service', () => {
  test('rejects unsupported method', async () => {
    const res = await processPayment({
      amount: 10,
      method: 'BITCOIN',
      details: {}
    });
    expect(res.success).toBe(false);
  });

  test('accepts valid card', async () => {
    jest.spyOn(Math, 'random').mockReturnValue(0.5);
    const res = await processPayment({
      amount: 10,
      method: 'CREDIT_CARD',
      details: { cardNumber: '4111111111111111', cvv: '123' }
    });
    expect(res.success).toBe(true);
    expect(res.transactionId).toBeDefined();
    Math.random.mockRestore();
  });
});
