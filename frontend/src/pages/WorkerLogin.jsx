import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Admin.css";

const LOGIN_URL = "http://127.0.0.1:8000/worker/login";

export default function WorkerLogin() {
  const [identifier, setIdentifier] = useState("");
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
        body: JSON.stringify({ identifier, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Incorrect Worker ID/Email or password");

      localStorage.setItem("worker_token", data.token);
      localStorage.setItem("worker_name", data.name);
      localStorage.setItem("worker_email", data.email);
      localStorage.setItem("worker_username", data.username);
      localStorage.setItem("worker_must_change_password", String(data.must_change_password));

      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center">
      <form className="admin-login-card" onSubmit={handleSubmit} autoComplete="off">
        <div className="admin-login-mark">MM</div>
        <div className="admin-login-title">Team sign-in</div>
        <div className="admin-login-subtitle">
          Meridian Manufacturing — use the Worker ID or email and password your admin gave you
        </div>

        <input
          className="admin-input"
          placeholder="Worker ID or Email"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
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
          {loading ? "Checking…" : "Sign in"}
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