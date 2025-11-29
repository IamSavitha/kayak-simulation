function validateCreditCard({ cardNumber, expiryMonth, expiryYear, cvv }) {
  if (!cardNumber || cardNumber.replace(/\D/g, '').length < 12) return false;
  if (!cvv || cvv.length < 3) return false;
  return true;
}

async function processPayment({ amount, method, details }) {
  await new Promise((res) => setTimeout(res, 200));

  if (method === 'CREDIT_CARD') {
    if (!validateCreditCard(details)) {
      return { success: false, error: 'Invalid credit card details' };
    }
  } else if (method === 'PAYPAL') {
    if (!details?.paypalEmail) {
      return { success: false, error: 'Missing PayPal email' };
    }
  } else {
    return { success: false, error: 'Unsupported payment method' };
  }

  if (Math.random() < 0.1) {
    return { success: false, error: 'Payment gateway error' };
  }

  const transactionId = `TX-${Date.now()}-${Math.floor(Math.random() * 9999)}`;
  return { success: true, transactionId };
}

module.exports = { processPayment };
