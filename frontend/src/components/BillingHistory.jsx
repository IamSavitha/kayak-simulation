import { useEffect, useState } from 'react';
import { getBillingForUser } from '../api/billingApi';

export default function BillingHistory({ userId, onSelectBilling }) {
  const [rows, setRows] = useState([]);

  useEffect(() => {
    if (!userId) return;
    getBillingForUser(userId).then(setRows);
  }, [userId]);

  return (
    <div className="billing-history">
      <h2>Billing History</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Type</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Invoice</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((b) => (
            <tr key={b.billing_id}>
              <td>{new Date(b.transaction_date).toLocaleString()}</td>
              <td>{b.booking_type}</td>
              <td>${Number(b.total_amount).toFixed(2)}</td>
              <td>{b.transaction_status}</td>
              <td>
                <button onClick={() => onSelectBilling(b.billing_id)}>
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
