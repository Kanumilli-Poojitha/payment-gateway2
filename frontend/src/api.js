import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
});

// Attach API credentials
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem("apiKey");
  const apiSecret = localStorage.getItem("apiSecret");

  if (apiKey && apiSecret) {
    config.headers["X-Api-Key"] = apiKey;
    config.headers["X-Api-Secret"] = apiSecret;
  }

  return config;
});

export default api;