// src/pages/Login.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    // Store email locally to simulate login
    localStorage.setItem("merchantEmail", email);
    navigate("/dashboard");
  };

  return (
    <form data-test-id="login-form" onSubmit={handleSubmit}>
      <input
        data-test-id="email-input"
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        data-test-id="password-input"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button data-test-id="login-button" type="submit">
        Login
      </button>
    </form>
  );
}