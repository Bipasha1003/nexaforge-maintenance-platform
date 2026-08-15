import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Admin.css";

const LOGIN_URL = "http://127.0.0.1:8000/worker/login";
const LAST_IDENTIFIER_KEY = "nexaforge_last_worker_identifier";

export default function WorkerLogin() {
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Prefill last-used Worker ID/email only — never the password.
  useEffect(() => {
    const saved = localStorage.getItem(LAST_IDENTIFIER_KEY);
    if (saved) setIdentifier(saved);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Incorrect Worker ID/Email or password");

      localStorage.setItem("worker_token", data.token);
      localStorage.setItem("worker_name", data.name);
      localStorage.setItem("worker_email", data.email);
      localStorage.setItem("worker_username", data.username);
      localStorage.setItem("worker_must_change_password", String(data.must_change_password));
      localStorage.setItem(LAST_IDENTIFIER_KEY, identifier);

      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center admin-shell-bg-worker">
      <form className="admin-login-card" onSubmit={handleSubmit}>
        <div className="admin-login-brand">
          <img
            src="/images/company-logo.png"
            alt="NexaForge"
            className="admin-login-logo"
          />
          <span className="admin-login-brand-name">NexaForge</span>
        </div>
        <div className="admin-login-title">Worker sign-in</div>
        <div className="admin-login-subtitle">
          Use the Worker ID or email and password your admin gave you
        </div>

        <input
          className="admin-input"
          placeholder="Worker ID or Email"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          autoComplete="username"
          autoFocus
        />

        <div style={{ position: "relative", width: "100%" }}>
          <input
            type={showPassword ? "text" : "password"}
            className="admin-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            style={{ width: "100%", paddingRight: "40px", boxSizing: "border-box" }}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="admin-pw-toggle"
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? "👁️‍🗨️" : "👁️"}
          </button>
        </div>

        {error && <div className="admin-error">{error}</div>}

        <button className="admin-btn admin-btn-primary" type="submit" disabled={loading}>
          {loading ? "Checking…" : "Sign in"}
        </button>

        <button
          type="button"
          className="admin-btn admin-btn-ghost admin-back-btn"
          onClick={() => navigate("/")}
        >
          Back to dashboard
        </button>
      </form>
    </div>
  );
}