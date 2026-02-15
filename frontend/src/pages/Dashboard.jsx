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
  const [webhooks, setWebhooks] = useState([]);
  const [newWebhookUrl, setNewWebhookUrl] = useState("");
  const [logs, setLogs] = useState([]);
  const [activeTab, setActiveTab] = useState("stats");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const merchantRes = await api.get("/test/merchant");
      const { api_key, api_secret } = merchantRes.data;
      setApiKey(api_key);
      setApiSecret(api_secret);

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

      fetchWebhooks();
      fetchLogs();
    } catch (err) {
      console.error("Dashboard load failed", err);
    }
  }

  async function fetchWebhooks() {
    try {
      const res = await api.get("/webhooks");
      setWebhooks(res.data);
    } catch (err) { console.error(err); }
  }

  async function fetchLogs() {
    try {
      const res = await api.get("/webhook-logs");
      setLogs(res.data);
    } catch (err) { console.error(err); }
  }

  async function handleAddWebhook() {
    if (!newWebhookUrl) return;
    try {
      await api.post("/webhooks", { url: newWebhookUrl });
      setNewWebhookUrl("");
      fetchWebhooks();
    } catch (err) { console.error(err); }
  }

  return (
    <div data-test-id="dashboard" style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Merchant Dashboard</h1>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button onClick={() => setActiveTab("stats")}>Stats</button>
        <button onClick={() => setActiveTab("webhooks")}>Webhooks</button>
        <button onClick={() => setActiveTab("logs")}>Delivery Logs</button>
        <button onClick={() => setActiveTab("docs")}>API Docs</button>
      </div>

      <div data-test-id="api-credentials" style={{ background: '#f5f5f5', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <h3>API Integration</h3>
        <div>
          <label>API Key: </label>
          <code data-test-id="api-key">{apiKey}</code>
        </div>
        <div style={{ marginTop: '5px' }}>
          <label>API Secret: </label>
          <code data-test-id="api-secret">{apiSecret}</code>
        </div>
      </div>

      {activeTab === "stats" && (
        <div data-test-id="stats-container" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
          <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px' }}>
            <h4>Total Transactions</h4>
            <div data-test-id="total-transactions" style={{ fontSize: '24px' }}>{stats.totalTransactions}</div>
          </div>
          <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px' }}>
            <h4>Total Volume</h4>
            <div data-test-id="total-amount" style={{ fontSize: '24px' }}>₹{(stats.totalAmount / 100).toLocaleString()}</div>
          </div>
          <div style={{ border: '1px solid #ddd', padding: '15px', borderRadius: '8px' }}>
            <h4>Success Rate</h4>
            <div data-test-id="success-rate" style={{ fontSize: '24px' }}>{stats.successRate}%</div>
          </div>
        </div>
      )}

      {activeTab === "webhooks" && (
        <div data-test-id="webhook-settings">
          <h3>Webhook Settings</h3>
          <div style={{ marginBottom: '15px' }}>
            <input
              type="text"
              placeholder="https://your-site.com/webhook"
              value={newWebhookUrl}
              onChange={(e) => setNewWebhookUrl(e.target.value)}
              style={{ padding: '8px', width: '300px' }}
            />
            <button onClick={handleAddWebhook} style={{ padding: '8px 15px', marginLeft: '10px' }}>Add Webhook</button>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid #eee' }}>
                <th style={{ padding: '10px' }}>URL</th>
                <th>Secret</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {webhooks.map(wh => (
                <tr key={wh.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '10px' }}>{wh.url}</td>
                  <td><code>{wh.secret}</code></td>
                  <td>{wh.active ? "Active" : "Inactive"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "logs" && (
        <div data-test-id="webhook-logs">
          <h3>Delivery Logs</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ textAlign: 'left', borderBottom: '1px solid #eee' }}>
                <th style={{ padding: '10px' }}>Topic</th>
                <th>Status</th>
                <th>Attempts</th>
                <th>Response</th>
                <th>Next Retry</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '10px' }}>{log.event}</td>
                  <td>{log.status}</td>
                  <td>{log.attempts}</td>
                  <td>{log.response_code}</td>
                  <td>{log.next_retry_at ? new Date(log.next_retry_at).toLocaleTimeString() : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === "docs" && (
        <div data-test-id="api-documentation">
          <h3>Integration Guide</h3>
          <p>Use our SDK to accept payments in your application.</p>
          <pre style={{ background: '#333', color: '#fff', padding: '15px', borderRadius: '8px' }}>
            {`<script src="http://localhost:8000/gateway.js"></script>
<script>
  GatewayCheckout.open({
    amount: 10000, // in paise
    currency: "INR",
    onSuccess: (p) => alert("Paid!"),
    onFailure: (p) => alert("Failed")
  });
</script>`}
          </pre>
          <h4>Endpoints</h4>
          <ul>
            <li><code>POST /payments</code> - Create a payment</li>
            <li><code>POST /refunds</code> - Initiate a refund</li>
            <li><code>GET /payments/:id</code> - Check payment status</li>
          </ul>
        </div>
      )}
    </div>
  );
}