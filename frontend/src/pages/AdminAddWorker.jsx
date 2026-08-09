import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Admin.css";

const GENERATE_URL = "http://127.0.0.1:8000/admin/workers";

export default function AdminAddWorker() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState("");
  const [address, setAddress] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("admin_token");

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(GENERATE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, email, phone, department, address }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Couldn't create that worker.");
      setCredentials(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (credentials) {
    return (
      <div className="admin-shell admin-shell-center">
        <div className="admin-login-card" style={{ maxWidth: 380 }}>
          <div className="admin-login-mark">✓</div>
          <div className="admin-login-title">Account created</div>
          <div className="admin-notice admin-notice-success" style={{ width: "100%", textAlign: "left" }}>
            <div><b>Employee ID:</b> {credentials.employee_code}</div>
            <div><b>Username:</b> {credentials.username}</div>
            <div><b>Temporary password:</b> {credentials.temp_password}</div>
          </div>
          <button className="admin-btn admin-btn-primary" onClick={() => navigate("/admin")}>
            Back to admin dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-shell admin-shell-center">
      <form className="admin-login-card" onSubmit={handleSubmit}>
        <div className="admin-login-mark">MM</div>
        <div className="admin-login-title">Add a worker</div>
        <input className="admin-input" placeholder="Full name (e.g. Subhra Mondal)" value={name} onChange={(e) => setName(e.target.value)} autoFocus required />
        <input type="email" className="admin-input" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="admin-input" placeholder="Phone number" value={phone} onChange={(e) => setPhone(e.target.value)} required />
        <input className="admin-input" placeholder="Department" value={department} onChange={(e) => setDepartment(e.target.value)} required />
        <input className="admin-input" placeholder="Home Address (Permanent)" value={address} onChange={(e) => setAddress(e.target.value)} required />
        
        {error && <div className="admin-error">{error}</div>}
        <button className="admin-btn admin-btn-primary" type="submit" disabled={loading}>
          {loading ? "Creating…" : "Generate credentials"}
        </button>
        <Link to="/admin" style={{ fontSize: 12.5, color: "var(--text-muted)" }}>Cancel</Link>
      </form>
    </div>
  );
}