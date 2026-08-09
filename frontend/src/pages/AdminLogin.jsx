import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Admin.css";

const LOGIN_URL = "http://127.0.0.1:8000/admin/login";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
      localStorage.setItem("admin_name", data.name); // Save the name from the backend

      navigate("/admin");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center">
      <form className="admin-login-card" onSubmit={handleSubmit} autoComplete="off">
        <div className="admin-login-mark">MX</div>
        <div className="admin-login-title">Admin access</div>
        <div className="admin-login-subtitle">Mill X500 maintenance agent</div>

        <input
          type="email"
          className="admin-input"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoComplete="off"
          autoFocus
        />
        
        <div style={{ position: "relative", width: "100%" }}>
          <input
            type={showPassword ? "text" : "password"}
            className="admin-input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="new-password"
            style={{ width: "100%", paddingRight: "40px", boxSizing: "border-box" }}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: "absolute",
              right: "12px",
              top: "50%",
              transform: "translateY(-50%)",
              background: "transparent",
              border: "none",
              cursor: "pointer",
              fontSize: "16px",
              color: "#aaa",
              padding: 0
            }}
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
          className="admin-btn" 
          onClick={() => navigate("/")}
          style={{ marginTop: "12px", background: "transparent", border: "1px solid #444", color: "#ccc" }}
        >
          Back to dashboard
        </button>
      </form>
    </div>
  );
}