(function (window) {
  const API_BASE = "http://localhost:8000/api/v1";
  const CHECKOUT_URL = "http://localhost:3001";

  function createModal() {
    const overlay = document.createElement("div");
    overlay.id = "gateway-overlay";
    overlay.setAttribute("data-test-id", "payment-modal");
    overlay.style.cssText = `
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.6);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 9999;
    `;

    const container = document.createElement("div");
    container.style.cssText = "position: relative; display: flex;";

    const closeBtn = document.createElement("button");
    closeBtn.textContent = "×";
    closeBtn.setAttribute("data-test-id", "close-modal-button");
    closeBtn.style.cssText = `
      position: absolute;
      top: -40px;
      right: 0;
      background: none;
      border: none;
      color: white;
      font-size: 32px;
      cursor: pointer;
    `;
    closeBtn.onclick = removeModal;

    const iframe = document.createElement("iframe");
    iframe.setAttribute("data-test-id", "payment-iframe");
    iframe.style.cssText = `
      width: 420px;
      height: 600px;
      border: none;
      border-radius: 12px;
      background: white;
    `;
    
    container.appendChild(closeBtn);
    container.appendChild(iframe);
    overlay.appendChild(container);
    document.body.appendChild(overlay);
    return { overlay, iframe };
  }

  function removeModal() {
    const el = document.getElementById("gateway-overlay");
    if (el) el.remove();
  }

  async function createOrder(options) {
    const res = await fetch(`${API_BASE}/orders/public`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: options.amount,
        currency: options.currency || "INR",
        notes: options.notes || {},
      }),
    });
    if (!res.ok) throw new Error("Order creation failed");
    return res.json();
  }

  function listenForMessages(handlers) {
    function handler(event) {
      if (!event.data || !event.data.type) return;
      switch (event.data.type) {
        case "CHECKOUT_READY":
          return;
        case "PAYMENT_SUCCESS":
          removeModal();
          handlers.onSuccess?.(event.data.payload);
          window.removeEventListener("message", handler);
          break;
        case "PAYMENT_FAILED":
          removeModal();
          handlers.onFailure?.(event.data.payload);
          window.removeEventListener("message", handler);
          break;
      }
    }
    window.addEventListener("message", handler);
  }

  window.GatewayCheckout = {
    open: async function (options) {
      if (!options?.amount) throw new Error("amount is required");

      const order = await createOrder(options);
      const { iframe } = createModal();
      iframe.src = `${CHECKOUT_URL}/?order_id=${order.id}`;
      listenForMessages(options);
    },
  };
})(window);