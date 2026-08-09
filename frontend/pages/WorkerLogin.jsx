import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Admin.css";

const LOGIN_URL = "http://127.0.0.1:8000/worker/login";

export default function WorkerLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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

      if (!res.ok) throw new Error("Incorrect email or password");
      const data = await res.json();

      localStorage.setItem("worker_token", data.token);
      localStorage.setItem("worker_name", data.name);
      localStorage.setItem("worker_email", data.email);
      navigate("/dashboard");
    } catch (err) {
      setError("Couldn't sign in. Check your email/password, or that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center">
      <form className="admin-login-card" onSubmit={handleSubmit}>
        <div className="admin-login-mark">MM</div>
        <div className="admin-login-title">Team sign-in</div>
        <div className="admin-login-subtitle">Meridian Manufacturing — maintenance console</div>

        <input
          type="email"
          className="admin-input"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          autoFocus
        />
        <input
          type="password"
          className="admin-input"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        {error && <div className="admin-error">{error}</div>}

        <button className="admin-btn admin-btn-primary" type="submit" disabled={loading}>
          {loading ? "Checking…" : "Sign in"}
        </button>

        <div style={{ fontSize: 12.5, color: "var(--text-muted)" }}>
          New here? <Link to="/register" style={{ color: "var(--accent)" }}>Create an account</Link>
        </div>
      </form>
    </div>
  );
}