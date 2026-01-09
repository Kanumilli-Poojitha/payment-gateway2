import { useEffect, useState } from "react";
import api from "../api";

export default function Dashboard() {
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const [stats, setStats] = useState({
    totalTransactions: 0,
    totalAmount: 0,
    successRate: 0,
  });

  useEffect(() => {
    async function loadDashboard() {
      try {
        const merchantRes = await api.get("/test/merchant");

        const { api_key, api_secret } = merchantRes.data;

        setApiKey(api_key);
        setApiSecret(api_secret);

        // store for reuse
        localStorage.setItem("apiKey", api_key);
        localStorage.setItem("apiSecret", api_secret);

        // 2️⃣ Fetch payments
        const paymentsRes = await api.get("/payments");

        const payments = paymentsRes.data;
        const total = payments.length;
        const success = payments.filter(p => p.status === "success").length;
        const amount = payments
          .filter(p => p.status === "success")
          .reduce((sum, p) => sum + p.amount, 0);

        setStats({
          totalTransactions: total,
          totalAmount: amount,
          successRate: total > 0 ? Math.round((success / total) * 100) : 0,
        });

      } catch (err) {
        console.error("Dashboard load failed", err);
      }
    }

    loadDashboard();
  }, []);

  return (
    <div data-test-id="dashboard">
      <div data-test-id="api-credentials">
        <div>
          <label>API Key</label>
          <span data-test-id="api-key">{apiKey}</span>
        </div>
        <div>
          <label>API Secret</label>
          <span data-test-id="api-secret">{apiSecret}</span>
        </div>
      </div>

      <div data-test-id="stats-container">
        <div data-test-id="total-transactions">{stats.totalTransactions}</div>
        <div data-test-id="total-amount">
          ₹{(stats.totalAmount / 100).toLocaleString()}
        </div>
        <div data-test-id="success-rate">{stats.successRate}%</div>
      </div>
    </div>
  );
}