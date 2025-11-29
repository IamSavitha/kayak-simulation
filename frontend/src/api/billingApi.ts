import axios from 'axios';

const billingApi = axios.create({
  baseURL: import.meta.env.VITE_BILLING_API || 'http://localhost:8005',
});

export async function createPayment(payload: any) {
  const res = await billingApi.post('/payments', payload);
  return res.data; 
}

export async function getBillingById(billingId: string) {
  const res = await billingApi.get(`/billings/${billingId}`);
  return res.data; 
}

export async function searchBillings(params: any) {
  const res = await billingApi.get('/billings', { params });
  return res.data; 
}

export async function getInvoice(billingId: string) {
  const res = await billingApi.get(`/billings/${billingId}/invoice`);
  return res.data; 
}

export async function refundBilling(billingId: string, body: any) {
  const res = await billingApi.post(`/billings/${billingId}/refund`, body);
  return res.data;
}
