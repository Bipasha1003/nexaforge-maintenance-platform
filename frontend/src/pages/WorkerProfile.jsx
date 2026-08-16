import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Admin.css";
import { API_BASE } from "../config";

const ME_URL = `${API_BASE}/worker/me`;
const PROFILE_URL = `${API_BASE}/worker/profile`;
const PASSWORD_URL = `${API_BASE}/worker/change-password`;

export default function WorkerProfile() {
  const [worker, setWorker] = useState(null);
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState("");
  const [profileNotice, setProfileNotice] = useState(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [passwordNotice, setPasswordNotice] = useState(null);
  const [changingPassword, setChangingPassword] = useState(false);

  const navigate = useNavigate();
  const token = localStorage.getItem("worker_token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    fetch(ME_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => {
        setWorker(data);
        setName(data.name || "");
        setUsername(data.username || "");
        setPhone(data.phone || "");
        setDepartment(data.department || "");
      })
      .catch(() => {});
  }, [token, navigate]);

  async function handleSaveProfile(e) {
    e.preventDefault();
    setProfileNotice(null);
    try {
      const res = await fetch(PROFILE_URL, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, username, phone, department }),
      });
      if (!res.ok) throw new Error();
      const updated = await res.json();
      
      // This updates the UI automatically!
      setWorker(updated);
      
      localStorage.setItem("worker_name", updated.name);
      localStorage.setItem("worker_username", updated.username); 
      
      setProfileNotice({ type: "success", text: "Profile saved." });
    } catch {
      setProfileNotice({ type: "error", text: "Couldn't save your profile." });
    }
  }

  async function handleChangePassword(e) {
    e.preventDefault();
    setChangingPassword(true);
    setPasswordNotice(null);
    try {
      const res = await fetch(PASSWORD_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Couldn't change your password.");

      localStorage.setItem("worker_must_change_password", "false");
      setWorker((w) => ({ ...w, must_change_password: false }));
      setCurrentPassword("");
      setNewPassword("");
      setPasswordNotice({ type: "success", text: "Password changed." });
    } catch (err) {
      setPasswordNotice({ type: "error", text: err.message });
    } finally {
      setChangingPassword(false);
    }
  }

  if (!worker) {
    return <div className="admin-shell">Loading…</div>;
  }

  return (
    <div className="admin-shell">
      <header className="admin-header">
        <div className="admin-header-title">My profile</div>
        <Link to="/dashboard" className="admin-btn admin-btn-ghost" style={{ textDecoration: "none" }}>
          Back to dashboard
        </Link>
      </header>

      {worker.must_change_password && (
        <div className="admin-notice admin-notice-error">
          This account is using a temporary password. Please set a new one below before continuing.
        </div>
      )}

      {/* --- ALL ACCOUNT DETAILS DISPLAYED HERE --- */}
      <div className="admin-drop" style={{ cursor: "default", textAlign: "left" }}>
        <div className="admin-drop-title" style={{ marginBottom: 10 }}>Account Details</div>
        <div style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.9 }}>
          <div><b style={{ color: "var(--text)" }}>Full Name:</b> {worker.name}</div>
          <div><b style={{ color: "var(--text)" }}>Username:</b> {worker.username}</div>
          <div><b style={{ color: "var(--text)" }}>Employee ID:</b> {worker.employee_code}</div>
          <div><b style={{ color: "var(--text)" }}>Department:</b> {worker.department || "—"}</div>
          <div><b style={{ color: "var(--text)" }}>Email:</b> {worker.email}</div>
          <div><b style={{ color: "var(--text)" }}>Phone:</b> {worker.phone || "—"}</div>
          {worker.address && <div><b style={{ color: "var(--text)" }}>Home Address:</b> {worker.address}</div>}
        </div>
      </div>

      {/* Editable Information */}
      <form className="admin-drop" style={{ cursor: "default", textAlign: "left" }} onSubmit={handleSaveProfile}>
        <div className="admin-drop-title" style={{ marginBottom: 10 }}>Edit profile</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 360 }}>
          <input className="admin-input" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
          <input className="admin-input" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input className="admin-input" placeholder="Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
          <input className="admin-input" placeholder="Department" value={department} onChange={(e) => setDepartment(e.target.value)} />
          
          {profileNotice && <div className={`admin-notice admin-notice-${profileNotice.type}`}>{profileNotice.text}</div>}
          <button className="admin-btn admin-btn-primary" type="submit">Save profile</button>
        </div>
      </form>

      <form className="admin-drop" style={{ cursor: "default", textAlign: "left" }} onSubmit={handleChangePassword}>
        <div className="admin-drop-title" style={{ marginBottom: 10 }}>Change password</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 10, maxWidth: 360 }}>
          <input
            type="password"
            className="admin-input"
            placeholder="Current password"
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
          />
          <input
            type="password"
            className="admin-input"
            placeholder="New password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          {passwordNotice && <div className={`admin-notice admin-notice-${passwordNotice.type}`}>{passwordNotice.text}</div>}
          <button className="admin-btn admin-btn-primary" type="submit" disabled={changingPassword}>
            {changingPassword ? "Changing…" : "Change password"}
          </button>
        </div>
      </form>
    </div>
  );
}