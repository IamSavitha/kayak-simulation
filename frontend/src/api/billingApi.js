import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_BILLING_API || 'http://localhost:4004'
});

export async function createBilling(body) {
  const res = await api.post('/billing', body);
  return res.data;
}

export async function getBillingForUser(userId) {
  const res = await api.get(`/billing/user/${userId}`);
  return res.data;
}

export async function getInvoice(billingId) {
  const res = await api.get(`/billing/${billingId}/invoice`);
  return res.data;
}
