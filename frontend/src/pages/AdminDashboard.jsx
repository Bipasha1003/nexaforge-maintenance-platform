import { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";
import "./PublicSite.css";
import "./Admin.css";

const DOCS_URL = "http://127.0.0.1:8000/admin/documents";
const DELETE_URL = "http://127.0.0.1:8000/admin/documents";
const UPLOAD_URL = "http://127.0.0.1:8000/admin/upload";
const WORKERS_URL = "http://127.0.0.1:8000/admin/workers";

// Starting fleet. There's no /admin/machines endpoint yet, so machines
// you add below live in this page's state and reset on refresh —
// say the word and I'll wire up a real table + route for these.
const SEED_FLEET = [
  { id: "mx500", name: "CNC Mill X500", type: "CNC Mill", status: "operational", lastCheckIn: "4 minutes ago", nextMaintenance: "Clean coolant tank strainer", nextMaintenanceDue: "Due in 12 days", openIssues: 0 },
  { id: "lathe-t999", name: "Fervi Gear Head Bench Lathe", type: "CNC Lathe", status: "warning", lastCheckIn: "22 minutes ago", nextMaintenance: "Adjust motor belt tension", nextMaintenanceDue: "Due in 4 days", openIssues: 1 },
  { id: "saw-cpo350", name: "Scotchman CPO-350 Cold Saw", type: "Cold Saw", status: "operational", lastCheckIn: "15 minutes ago", nextMaintenance: "Check regulator water-trap filter", nextMaintenanceDue: "Due in 30 days", openIssues: 0 },
  { id: "grind-kgs", name: "Kent Precision Surface Grinder", type: "Surface Grinder", status: "operational", lastCheckIn: "1 hour ago", nextMaintenance: "Clean hydraulic tank & change oil", nextMaintenanceDue: "Due in 5 days", openIssues: 0 },
  { id: "press-p001", name: "Fervi 20-Ton Hydraulic Press", type: "Hydraulic Press", status: "critical", lastCheckIn: "1 hour ago", nextMaintenance: "Check hydraulic oil level", nextMaintenanceDue: "Overdue by 2 days", openIssues: 2 },
];

const STATUS_LABEL = { operational: "Operational", warning: "Needs attention", critical: "Critical" };

function fleetSummary(fleet) {
  const operational = fleet.filter((m) => m.status === "operational").length;
  const needsAttention = fleet.filter((m) => m.status !== "operational").length;
  const openIssues = fleet.reduce((sum, m) => sum + m.openIssues, 0);
  return { total: fleet.length, operational, needsAttention, openIssues };
}

function greetingForHour(hour) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

// Boxed nav button style, shared by the three "+ Add ___" actions so
// they read as clear, clickable boxes against the background photo
// instead of loose colored text.
const navBoxBtn = {
  background: "rgba(255, 255, 255, 0.9)",
  border: "1.5px solid var(--border)",
  borderRadius: 10,
  cursor: "pointer",
  fontFamily: '"Inter", sans-serif',
  fontSize: "15px",
  fontWeight: 700,
  padding: "10px 18px",
  color: "var(--l-accent)",
};

export default function AdminDashboard() {
  const [docs, setDocs] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [fleet, setFleet] = useState(SEED_FLEET);
  const [chatSignal, setChatSignal] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);
  const [showAddMachine, setShowAddMachine] = useState(false);
  const [showAddDocument, setShowAddDocument] = useState(false);
  const [showAddWorker, setShowAddWorker] = useState(false);
  const [fleetNotice, setFleetNotice] = useState(null);
  const navigate = useNavigate();
  const summary = fleetSummary(fleet);

  const token = localStorage.getItem("admin_token");
  const adminName = localStorage.getItem("admin_name") || "Admin";
  const firstName = adminName.split(" ")[0];

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const fetchData = useCallback(async () => {
    if (!token) return;
    try {
      const [docsRes, workersRes] = await Promise.all([
        fetch(DOCS_URL, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(WORKERS_URL, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (docsRes.ok) setDocs(await docsRes.json());
      if (workersRes.ok) setWorkers(await workersRes.json());
    } catch {
      // silent catch for interval polling
    }
  }, [token]);

  useEffect(() => {
    if (!token) { navigate("/admin/login"); return; }
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [token, navigate, fetchData]);

  async function handleDeleteDoc(docId) {
    await fetch(`${DELETE_URL}/${docId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    fetchData();
  }

  async function handleDeleteWorker(workerId) {
    await fetch(`${WORKERS_URL}/${workerId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    fetchData();
  }

  function handleAddMachine(machine) {
    const id = `${machine.name.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-${Date.now()}`;
    setFleet((prev) => [...prev, { ...machine, id, lastCheckIn: "Just added", openIssues: 0 }]);
    setShowAddMachine(false);
    setFleetNotice({ type: "success", text: `${machine.name} added to the fleet.` });
    setTimeout(() => setFleetNotice(null), 4000);
  }

  function handleRemoveMachine(id) {
    setFleet((prev) => prev.filter((m) => m.id !== id));
  }

  function handleLogout() {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_email");
    localStorage.removeItem("admin_name");
    navigate("/"); 
  }

  const handleDownload = (e, docName) => {
    e.preventDefault();
    alert(`Downloading ${docName}... (Simulated download)`);
  };

  const heroLine = useMemo(() => {
    if (summary.needsAttention === 0) {
      return `All ${summary.total} machines on the floor are running clean. Nothing waiting on you right now.`;
    }
    return `${summary.operational} of ${summary.total} machines are running clean today. ${summary.openIssues === 1 ? "One open issue is" : `${summary.openIssues} open issues are`} waiting on the floor.`;
  }, [summary]);

  return (
    <div className="site site-bg-admin">
      {/* Sticky Header */}
      <header className={`site-header ${isScrolled ? "scrolled" : ""}`}>
        <div className="site-brand" onClick={() => navigate("/")} style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: "12px" }}>
          <img 
            src="/images/company-logo.png" 
            alt="NexaForge Logo" 
            style={{ width: "40px", height: "40px", objectFit: "contain", filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" }} 
          />
          <div>
            <div style={{ fontFamily: '"Fraunces", serif', fontSize: '27px', fontWeight: 600, color: '#1c1a17' }}>NexaForge</div>
            <div style={{ fontFamily: '"Inter", sans-serif', fontSize: '13px', color: '#6b6459' }}>Admin Mode: {adminName}</div>
          </div>
        </div>
        <nav className="site-nav" style={{ fontFamily: '"Inter", sans-serif', fontSize: '15px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '14px', flexWrap: "wrap" }}>
          <button 
            onClick={() => setChatSignal((n) => n + 1)}
            style={{ ...navBoxBtn, background: "var(--accent)", color: "var(--accent-ink)", border: "none" }}
          >
            Open AI
          </button>

          <button type="button" onClick={() => setShowAddDocument(true)} style={navBoxBtn}>
            + Add Document
          </button>

          <button type="button" onClick={() => setShowAddMachine(true)} style={navBoxBtn}>
            + Add Machine
          </button>

          <button type="button" onClick={() => setShowAddWorker(true)} style={navBoxBtn}>
            + Add Worker
          </button>
          
          <span style={{ color: "var(--text)", fontWeight: 700, fontSize: 15, marginLeft: "6px", marginRight: "2px" }}>
            {adminName}
          </span>

          <button type="button" onClick={handleLogout} style={{ ...navBoxBtn, color: "var(--text-muted)" }}>
            Log out
          </button>
        </nav>
      </header>

      <main className="site-main" style={{ marginTop: 36, maxWidth: 1240, marginInline: "auto", width: "100%", paddingInline: 24 }}>

        {/* Hero */}
        <section
          style={{
            background: "rgba(255, 255, 255, 0.95)",
            backdropFilter: "blur(6px)",
            border: "1px solid var(--border)",
            borderRadius: 18,
            padding: "44px 44px",
            marginBottom: 36,
            boxShadow: "0 18px 40px rgba(28, 26, 23, 0.12)",
          }}
        >
          <div
            style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 13,
              letterSpacing: "0.1em",
              textTransform: "uppercase",
              color: "var(--l-accent)",
              marginBottom: 14,
              fontWeight: 600,
            }}
          >
            Operations overview
          </div>
          <h1
            style={{
              fontFamily: '"Fraunces", serif',
              fontWeight: 600,
              fontSize: "clamp(32px, 4vw, 50px)",
              lineHeight: 1.1,
              margin: "0 0 16px",
              color: "var(--text)",
            }}
          >
            {greetingForHour(new Date().getHours())}, {firstName}.
          </h1>
          <p style={{ fontFamily: '"Inter", sans-serif', fontSize: 18, lineHeight: 1.6, color: "var(--text-muted)", margin: 0, maxWidth: 680 }}>
            {heroLine}
          </p>
        </section>

        <div className="site-grid" style={{ gap: 20 }}>
          <section className="card" style={{ padding: 26, borderRadius: 14 }}>
            <div className="card-label" style={{ fontSize: 15 }}>Fleet status</div>
            <div className="card-value ok" style={{ fontSize: 30, marginTop: 6 }}>{summary.operational}/{summary.total} operational</div>
            <div className="kpi-sub" style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 6 }}>{summary.needsAttention} machine(s) need attention</div>
          </section>
          <section className="card" style={{ padding: 26, borderRadius: 14 }}>
            <div className="card-label" style={{ fontSize: 15 }}>Open issues</div>
            <div className="card-value" style={{ fontSize: 30, marginTop: 6 }}>{summary.openIssues}</div>
            <div className="kpi-sub" style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 6 }}>Across all fleet units</div>
          </section>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 40, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Equipment fleet</div>
          <button
            type="button"
            onClick={() => setShowAddMachine(true)}
            style={navBoxBtn}
          >
            + Add machine
          </button>
        </div>

        {fleetNotice && (
          <div className={`admin-notice admin-notice-${fleetNotice.type}`} style={{ marginBottom: 16, fontSize: 14, padding: "12px 16px" }}>
            {fleetNotice.text}
          </div>
        )}

        <div className="site-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: 20 }}>
          {fleet.map((m) => (
            <section key={m.id} className="card fleet-tile" style={{ padding: 26, borderRadius: 14, minHeight: 190 }}>
              <div className="fleet-tile-top" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div className="card-label" style={{ marginBottom: 4, fontSize: 16, fontWeight: 700, color: "var(--text)" }}>{m.name}</div>
                  <div className="fleet-type" style={{ fontSize: 14, color: "var(--text-muted)" }}>{m.type}</div>
                </div>
                <div className="fleet-status" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className={`status-dot ${m.status}`} />
                  <span className={`status-text ${m.status}`} style={{ fontSize: 13, fontWeight: 600 }}>{STATUS_LABEL[m.status]}</span>
                </div>
              </div>
              <div style={{ marginTop: 18, fontSize: 14, color: "var(--text-muted)", borderTop: "1px dashed var(--border)", paddingTop: 14 }}>
                <div style={{ marginBottom: 4 }}>Next service: <b style={{ color: "var(--text)" }}>{m.nextMaintenance}</b></div>
                <div style={{ color: m.status === 'critical' ? 'var(--danger)' : 'inherit', fontWeight: 600 }}>{m.nextMaintenanceDue}</div>
              </div>
              <div style={{ marginTop: 16, textAlign: "right" }}>
                <button className="admin-btn admin-btn-danger-ghost" style={{ fontSize: 13.5, padding: "7px 14px" }} onClick={() => handleRemoveMachine(m.id)}>Remove</button>
              </div>
            </section>
          ))}

          <button
            type="button"
            onClick={() => setShowAddMachine(true)}
            className="card fleet-tile"
            style={{
              padding: 26,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 10,
              minHeight: 190,
              borderRadius: 14,
              border: "2px dashed var(--border)",
              background: "rgba(255, 255, 255, 0.7)",
              color: "var(--text-muted)",
              cursor: "pointer",
              fontFamily: '"Inter", sans-serif',
              fontSize: 15,
              fontWeight: 600,
            }}
          >
            <span style={{ fontFamily: '"Fraunces", serif', fontSize: 32, lineHeight: 1 }}>+</span>
            Add a machine to the fleet
          </button>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 56, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Manual Library</div>
          <button type="button" onClick={() => setShowAddDocument(true)} style={navBoxBtn}>
            + Add document
          </button>
        </div>
        <div style={{ background: "#ffffff", borderRadius: 14, border: "1px solid var(--border)", overflow: "hidden", boxShadow: "0 12px 28px rgba(28, 26, 23, 0.08)" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 15 }}>
            <thead>
              <tr style={{ background: "#f5f3ef", textAlign: "left" }}>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Document</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Status</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Pages</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Action</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}></th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "18px 24px", fontWeight: 500 }}>{doc.name}</td>
                  <td style={{ padding: "18px 24px" }}><span className={`status-pill status-${doc.status}`} style={{ fontSize: 12.5, padding: "4px 12px" }}>{doc.status}</span></td>
                  <td style={{ padding: "18px 24px" }}>{doc.pages ?? "—"}</td>
                  <td style={{ padding: "18px 24px" }}>
                    <a href="#" onClick={(e) => handleDownload(e, doc.name)} style={{ fontSize: 14, textDecoration: "none", color: "var(--l-accent)", fontWeight: 600 }}>
                      ⬇ Download
                    </a>
                  </td>
                  <td style={{ padding: "18px 24px", textAlign: "right" }}><button className="admin-btn admin-btn-danger-ghost" style={{ fontSize: 13.5, padding: "7px 14px" }} onClick={() => handleDeleteDoc(doc.id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 56, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Team Directory</div>
          <button type="button" onClick={() => setShowAddWorker(true)} style={navBoxBtn}>
            + Add worker
          </button>
        </div>
        <div style={{ background: "#ffffff", borderRadius: 14, border: "1px solid var(--border)", overflow: "hidden", boxShadow: "0 12px 28px rgba(28, 26, 23, 0.08)" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 15 }}>
            <thead>
              <tr style={{ background: "#f5f3ef", textAlign: "left" }}>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>ID</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Name</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Dept</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Status</th>
                <th style={{ padding: "16px 24px", fontSize: 13, textAlign: "right" }}></th>
              </tr>
            </thead>
            <tbody>
              {workers.map((w) => (
                <tr key={w.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "18px 24px", fontWeight: 600 }}>W-{String(w.employee_no).padStart(4, "0")}</td>
                  <td style={{ padding: "18px 24px" }}>
                    <div style={{ fontWeight: 500 }}>{w.name}</div>
                    <div style={{ fontSize: 13, color: "var(--text-muted)" }}>{w.email}</div>
                  </td>
                  <td style={{ padding: "18px 24px" }}>{w.department || "—"}</td>
                  <td style={{ padding: "18px 24px" }}><span className={`status-pill ${w.must_change_password ? "status-processing" : "status-ready"}`} style={{ fontSize: 12.5, padding: "4px 12px" }}>{w.must_change_password ? "Pending Login" : "Active"}</span></td>
                  <td style={{ padding: "18px 24px", textAlign: "right" }}><button className="admin-btn admin-btn-danger-ghost" style={{ fontSize: 13.5, padding: "7px 14px" }} onClick={() => handleDeleteWorker(w.id)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
      
      {/* Dark Footer matching landing page */}
      <footer className="landing-footer" style={{ backgroundColor: "#1c1a17", color: "#e4dfd5", padding: "64px 40px 24px", marginTop: "72px" }}>
        <div className="footer-content" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "40px", maxWidth: "1200px", margin: "0 auto", paddingBottom: "40px" }}>
          <div className="footer-section">
            <div className="footer-brand" style={{ display: "flex", alignItems: "center", gap: "12px", fontFamily: "'Fraunces', serif", fontSize: "24px", fontWeight: 600, color: "#ffffff", marginBottom: "18px" }}>
              <img src="/images/company-logo.png" alt="NexaForge Logo" style={{ width: "34px", height: "34px", objectFit: "contain", filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" }} />
              <span>NexaForge</span>
            </div>
            <p style={{ lineHeight: 1.7, fontSize: 15 }}>
              Precision manufacturing backed by instant digital maintenance insights. 
              Bridging the gap between traditional metalworking and smart floor technology.
            </p>
          </div>
          
          <div className="footer-section">
            <h4 style={{ color: "#ffffff", fontFamily: "'Fraunces', serif", fontSize: "17px", marginBottom: "18px" }}>Quick Links</h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: 15 }}>
              <li style={{ marginBottom: "14px" }}><Link to="/admin" style={{ color: "#e4dfd5", textDecoration: "none" }}>Admin Console</Link></li>
              <li style={{ marginBottom: "14px" }}><Link to="/dashboard" style={{ color: "#e4dfd5", textDecoration: "none" }}>Worker Fleet Console</Link></li>
              <li style={{ marginBottom: "14px" }}><Link to="/" style={{ color: "#e4dfd5", textDecoration: "none" }}>Main Website</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 style={{ color: "#ffffff", fontFamily: "'Fraunces', serif", fontSize: "17px", marginBottom: "18px" }}>Contact Us</h4>
            <p style={{ marginBottom: "12px", fontSize: 15 }}>📍 123 Industrial Parkway</p>
            <p style={{ marginBottom: "12px", fontSize: 15 }}>📞 (555) 019-2834</p>
            <p style={{ marginBottom: "12px", fontSize: 15 }}>✉️ operations@nexaforge.com</p>
          </div>
        </div>
        
        <div className="footer-bottom" style={{ textAlign: "center", paddingTop: "24px", borderTop: "1px solid #36322d", fontSize: "14px", maxWidth: "1200px", margin: "0 auto", color: "#9c9284" }}>
          © 2026 NexaForge · Internal Operations & Maintenance Intelligence Platform
        </div>
      </footer>

      {showAddMachine && (
        <AddMachineModal onClose={() => setShowAddMachine(false)} onAdd={handleAddMachine} />
      )}

      {showAddDocument && (
        <AddDocumentModal
          token={token}
          onClose={() => setShowAddDocument(false)}
          onUploaded={() => {
            setShowAddDocument(false);
            fetchData();
          }}
        />
      )}

      {showAddWorker && (
        <AddWorkerModal
          token={token}
          onClose={() => setShowAddWorker(false)}
          onCreated={() => {
            fetchData();
          }}
        />
      )}

      <ChatWidget openSignal={chatSignal} />
    </div>
  );
}

/* ---------- Shared brand row used at the top of every "Add ___" modal ---------- */
function ModalBrand() {
  return (
    <div className="admin-login-brand" style={{ justifyContent: "center" }}>
      <img src="/images/company-logo.png" alt="NexaForge" className="admin-login-logo" style={{ width: 40, height: 40 }} />
      <span className="admin-login-brand-name" style={{ fontSize: 22 }}>NexaForge</span>
    </div>
  );
}

const modalLabel = { fontSize: 14.5, fontWeight: 700, color: "var(--text)", display: "flex", flexDirection: "column", gap: 7 };
const modalInput = { fontSize: 15, padding: "12px 14px" };

/* ---------- Add Machine ---------- */
function AddMachineModal({ onClose, onAdd }) {
  const [name, setName] = useState("");
  const [type, setType] = useState("");
  const [status, setStatus] = useState("operational");
  const [nextMaintenance, setNextMaintenance] = useState("");
  const [nextMaintenanceDue, setNextMaintenanceDue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!name.trim() || !type.trim()) return;
    onAdd({
      name: name.trim(),
      type: type.trim(),
      status,
      nextMaintenance: nextMaintenance.trim() || "No task scheduled yet",
      nextMaintenanceDue: nextMaintenanceDue.trim() || "No date set",
    });
  }

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <form className="admin-login-card" style={{ width: 440, alignItems: "stretch", textAlign: "left", padding: 34, gap: 16 }} onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <ModalBrand />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div className="admin-login-title" style={{ fontSize: 20 }}>Add a machine</div>
          <button type="button" onClick={onClose} aria-label="Close" style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "var(--text-muted)" }}>×</button>
        </div>

        <label style={modalLabel}>
          Machine name
          <input className="admin-input" style={modalInput} placeholder="e.g. Haas VF-2 Vertical Mill" value={name} onChange={(e) => setName(e.target.value)} autoFocus required />
        </label>

        <label style={modalLabel}>
          Type
          <input className="admin-input" style={modalInput} placeholder="e.g. CNC Mill" value={type} onChange={(e) => setType(e.target.value)} required />
        </label>

        <label style={modalLabel}>
          Status
          <select className="admin-input" style={modalInput} value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="operational">Operational</option>
            <option value="warning">Needs attention</option>
            <option value="critical">Critical</option>
          </select>
        </label>

        <label style={modalLabel}>
          Next service task
          <input className="admin-input" style={modalInput} placeholder="e.g. Replace coolant filter" value={nextMaintenance} onChange={(e) => setNextMaintenance(e.target.value)} />
        </label>

        <label style={modalLabel}>
          Due
          <input className="admin-input" style={modalInput} placeholder="e.g. Due in 14 days" value={nextMaintenanceDue} onChange={(e) => setNextMaintenanceDue(e.target.value)} />
        </label>

        <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 6 }}>
          <button type="button" className="admin-btn admin-btn-ghost" style={{ fontSize: 14.5, padding: "10px 20px" }} onClick={onClose}>Cancel</button>
          <button type="submit" className="admin-btn admin-btn-primary" style={{ width: "auto", fontSize: 14.5, padding: "10px 22px" }}>Add to fleet</button>
        </div>
      </form>
    </div>
  );
}

/* ---------- Add Document ---------- */
function AddDocumentModal({ token, onClose, onUploaded }) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState(null);
  const fileInputRef = useRef(null);

  async function handleFiles(files) {
    const file = files?.[0];
    if (!file) return;

    const allowedTypes = ["application/pdf", "text/plain", "image/jpeg", "image/png"];
    if (!allowedTypes.includes(file.type)) {
      setNotice({ type: "error", text: "Please upload a PDF, TXT, PNG, or JPG file." });
      return;
    }

    setUploading(true);
    setNotice(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(UPLOAD_URL, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) throw new Error();
      setNotice({ type: "success", text: `${file.name} uploaded. Processing in background.` });
      setTimeout(() => onUploaded(), 1200);
    } catch {
      setNotice({ type: "error", text: "Upload failed — check backend terminal." });
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <div className="admin-login-card" style={{ maxWidth: 480, padding: 34, gap: 16 }} onClick={(e) => e.stopPropagation()}>
        <ModalBrand />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
          <div className="admin-login-title" style={{ fontSize: 20 }}>Add a document</div>
          <button type="button" onClick={onClose} aria-label="Close" style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "var(--text-muted)" }}>×</button>
        </div>

        <div
          className={`admin-drop ${dragOver ? "admin-drop-active" : ""}`}
          style={{ width: "100%", padding: "48px 20px" }}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf, .txt, .png, .jpg, .jpeg"
            hidden
            onChange={(e) => handleFiles(e.target.files)}
          />
          <div className="admin-drop-title" style={{ fontSize: 16 }}>
            {uploading ? "Uploading…" : "Drop a PDF, text file, or image here, or click to browse"}
          </div>
        </div>

        {notice && <div className={`admin-notice admin-notice-${notice.type}`} style={{ width: "100%", fontSize: 14 }}>{notice.text}</div>}

        <button className="admin-btn admin-btn-ghost" style={{ width: "100%", fontSize: 14.5, padding: "11px 0" }} onClick={onClose}>
          Cancel
        </button>
      </div>
    </div>
  );
}

/* ---------- Add Worker ---------- */
function AddWorkerModal({ token, onClose, onCreated }) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [department, setDepartment] = useState("");
  const [address, setAddress] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(WORKERS_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, email, phone, department, address }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Couldn't create that worker.");
      setCredentials(data);
      onCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (credentials) {
    return (
      <div className="admin-modal-overlay" onClick={onClose}>
        <div className="admin-login-card" style={{ maxWidth: 420, padding: 34, gap: 16 }} onClick={(e) => e.stopPropagation()}>
          <div className="admin-login-mark" style={{ background: "var(--success)", color: "#fff", fontSize: 22 }}>✓</div>
          <div className="admin-login-title" style={{ fontSize: 20 }}>Account created</div>
          <div className="admin-notice admin-notice-success" style={{ width: "100%", textAlign: "left", fontSize: 14.5, lineHeight: 1.8 }}>
            <div><b>Employee ID:</b> {credentials.employee_code}</div>
            <div><b>Username:</b> {credentials.username}</div>
            <div><b>Temporary password:</b> {credentials.temp_password}</div>
          </div>
          <button className="admin-btn admin-btn-primary" style={{ fontSize: 14.5, padding: "11px 0" }} onClick={onClose}>
            Back to dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-modal-overlay" onClick={onClose}>
      <form className="admin-login-card" style={{ padding: 34, gap: 14 }} onClick={(e) => e.stopPropagation()} onSubmit={handleSubmit}>
        <ModalBrand />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" }}>
          <div className="admin-login-title" style={{ fontSize: 20 }}>Add a worker</div>
          <button type="button" onClick={onClose} aria-label="Close" style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "var(--text-muted)" }}>×</button>
        </div>

        <input className="admin-input" style={modalInput} placeholder="Full name (e.g. Subhra Mondal)" value={name} onChange={(e) => setName(e.target.value)} autoFocus required />
        <input type="email" className="admin-input" style={modalInput} placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="admin-input" style={modalInput} placeholder="Phone number" value={phone} onChange={(e) => setPhone(e.target.value)} required />
        <input className="admin-input" style={modalInput} placeholder="Department" value={department} onChange={(e) => setDepartment(e.target.value)} required />
        <input className="admin-input" style={modalInput} placeholder="Home Address (Permanent)" value={address} onChange={(e) => setAddress(e.target.value)} required />

        {error && <div className="admin-error" style={{ fontSize: 14 }}>{error}</div>}
        <button className="admin-btn admin-btn-primary" style={{ fontSize: 14.5, padding: "11px 0" }} type="submit" disabled={loading}>
          {loading ? "Creating…" : "Generate credentials"}
        </button>
        <button type="button" className="admin-btn admin-btn-ghost" style={{ width: "100%", fontSize: 14.5, padding: "11px 0" }} onClick={onClose}>
          Cancel
        </button>
      </form>
    </div>
  );
}