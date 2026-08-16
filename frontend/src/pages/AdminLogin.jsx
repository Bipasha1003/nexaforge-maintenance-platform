import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./Admin.css";
import { API_BASE } from "../config";

const LOGIN_URL = `${API_BASE}/admin/login`;
const LAST_EMAIL_KEY = "nexaforge_last_admin_email";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Prefill last-used email only. Never prefill password from app storage —
  // let the browser's own password manager handle that (see autoComplete below).
  useEffect(() => {
    const savedEmail = localStorage.getItem(LAST_EMAIL_KEY);
    if (savedEmail) setEmail(savedEmail);
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(LOGIN_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Incorrect email or password");

      localStorage.setItem("admin_token", data.token);
      localStorage.setItem("admin_email", data.email);
      localStorage.setItem("admin_name", data.name);
      localStorage.setItem(LAST_EMAIL_KEY, email);

      navigate("/admin");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center admin-shell-bg-admin">
      <form className="admin-login-card" onSubmit={handleSubmit}>
        <div className="admin-login-brand">
          <img
            src="/images/company-logo.png"
            alt="NexaForge"
            className="admin-login-logo"
          />
          <span className="admin-login-brand-name">NexaForge</span>
        </div>
        <div className="admin-login-title">Admin access</div>
        <div className="admin-login-subtitle">Fleet Console</div>

        <input
          type="email"
          className="admin-input"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
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
          {loading ? "Checking…" : "Log in"}
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