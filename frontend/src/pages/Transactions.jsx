import { useEffect, useState } from "react";
import api from "../api";

export default function Transactions() {
  const [payments, setPayments] = useState([]);

  useEffect(() => {
    api.get("/payments")
      .then(res => setPayments(res.data))
      .catch(err => console.error("Failed to load payments", err));
  }, []);

  return (
    <table data-test-id="transactions-table">
      <thead>
        <tr>
          <th>Payment ID</th>
          <th>Order ID</th>
          <th>Amount</th>
          <th>Method</th>
          <th>Status</th>
          <th>Created</th>
        </tr>
      </thead>
      <tbody>
        {payments.map(p => (
          <tr key={p.id} data-test-id="transaction-row">
            <td data-test-id="payment-id">{p.id}</td>
            <td data-test-id="order-id">{p.order_id}</td>
            <td data-test-id="amount">₹{p.amount / 100}</td>
            <td data-test-id="method">{p.method}</td>
            <td data-test-id="status">{p.status}</td>
            <td data-test-id="created-at">
              {new Date(p.created_at).toLocaleString()}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}