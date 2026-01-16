import { useEffect, useState } from "react";
import axios from "axios";
import { useSearchParams } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

const STATUS = { IDLE: "IDLE", PROCESSING: "PROCESSING", SUCCESS: "SUCCESS", FAILED: "FAILED" };

export default function Checkout() {
  const [searchParams] = useSearchParams();
  const orderId = searchParams.get("order_id");

  const [order, setOrder] = useState(null);
  const [method, setMethod] = useState("");
  const [status, setStatus] = useState(STATUS.IDLE);
  const [paymentId, setPaymentId] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  // notify SDK
  useEffect(() => window.parent.postMessage({ type: "CHECKOUT_READY" }, "*"), []);

  // fetch order
  useEffect(() => {
    if (!orderId) return;
    axios.get(`${API_BASE}/orders/public/${orderId}`)
      .then((res) => setOrder(res.data))
      .catch(() => { setStatus(STATUS.FAILED); setErrorMessage("Invalid order"); });
  }, [orderId]);

  // poll payment
  useEffect(() => {
    if (!paymentId || status !== STATUS.PROCESSING) return;
    const interval = setInterval(async () => {
      try {
        const res = await axios.get(`${API_BASE}/payments/public/${paymentId}`);
        if (res.data.status === "SUCCESS") {
          setStatus(STATUS.SUCCESS);
          window.parent.postMessage({ type: "PAYMENT_SUCCESS", payload: res.data }, "*");
          clearInterval(interval);
        }
        if (res.data.status === "FAILED") {
          setStatus(STATUS.FAILED);
          window.parent.postMessage({ type: "PAYMENT_FAILED", payload: res.data }, "*");
          clearInterval(interval);
        }
      } catch {
        setStatus(STATUS.FAILED);
        window.parent.postMessage({ type: "PAYMENT_FAILED" }, "*");
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [paymentId, status]);

  const createPayment = async (payload) => {
    setStatus(STATUS.PROCESSING);
    setErrorMessage("");
    try {
      const res = await axios.post(`${API_BASE}/payments/public`, payload);
      setPaymentId(res.data.id); // ✅ use payment id for polling
    } catch {
      setStatus(STATUS.FAILED);
      setErrorMessage("Payment failed");
      window.parent.postMessage({ type: "PAYMENT_FAILED" }, "*");
    }
  };

  if (!order) return <div>Loading checkout...</div>;

  return (
    <div data-test-id="checkout-container">
      <h3 data-test-id="order-amount">Pay ₹{(order.amount / 100).toFixed(2)}</h3>

      {status === STATUS.IDLE && (
        <>
          <div data-test-id="payment-methods">
            <button onClick={() => setMethod("upi")}>UPI</button>
            <button onClick={() => setMethod("card")}>Card</button>
          </div>

          {method === "upi" && (
            <form onSubmit={(e) => { e.preventDefault(); createPayment({ order_id: order.id, method: "upi", vpa: e.target.vpa.value }); }}>
              <input name="vpa" placeholder="user@bank" required />
              <button type="submit">Pay</button>
            </form>
          )}

          {method === "card" && (
            <form onSubmit={(e) => { e.preventDefault(); createPayment({ order_id: order.id, method: "card", card: { number: e.target.cardNumber.value, expiry_month: 12, expiry_year: 2030, cvv: "123" } }); }}>
              <input name="cardNumber" required />
              <button type="submit">Pay</button>
            </form>
          )}
        </>
      )}

      {status === STATUS.PROCESSING && <p data-test-id="processing-state">Processing payment...</p>}
      {status === STATUS.FAILED && <p data-test-id="error-state">{errorMessage}</p>}
    </div>
  );
}