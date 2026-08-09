import { useState, useEffect, useCallback } from "react";
import { useNavigate, Link } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";
import "./PublicSite.css";
import "./Admin.css";

const DOCS_URL = "http://127.0.0.1:8000/admin/documents";
const DELETE_URL = "http://127.0.0.1:8000/admin/documents";
const WORKERS_URL = "http://127.0.0.1:8000/admin/workers";

const FLEET = [
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

export default function AdminDashboard() {
  const [docs, setDocs] = useState([]);
  const [workers, setWorkers] = useState([]);
  const [chatSignal, setChatSignal] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();
  const summary = fleetSummary(FLEET);

  const token = localStorage.getItem("admin_token");
  const adminName = localStorage.getItem("admin_name") || "Admin";

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

  return (
    <div className="site">
      {/* Sticky Header */}
      <header className={`site-header ${isScrolled ? "scrolled" : ""}`}>
        <div className="site-brand" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
          <img 
            src="/images/company-logo.png" 
            alt="NexaForge Logo" 
            style={{ width: "36px", height: "36px", objectFit: "contain", filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" }} 
          />
          <div style={{ marginLeft: "12px" }}>
            <div className="site-title">NexaForge</div>
            <div className="site-subtitle">Admin Mode: {adminName}</div>
          </div>
        </div>
        <nav className="site-nav">
          <button className="hero-btn hero-btn-primary" onClick={() => setChatSignal((n) => n + 1)}>Open AI</button>
          
          <Link to="/admin/documents/new" className="site-nav-item site-nav-admin" style={{ marginLeft: 16 }}>+ Add Document</Link>
          
          <Link to="/admin/workers/new" className="site-nav-item site-nav-admin">+ Add Worker</Link>
          
          <span className="site-nav-item" style={{ color: "var(--l-accent)", fontWeight: 600, marginLeft: "16px", marginRight: "8px", pointerEvents: "none" }}>
            {adminName}
          </span>

          <span className="site-nav-item site-nav-admin" onClick={handleLogout} style={{ cursor: "pointer", marginLeft: 16 }}>Log out</span>
        </nav>
      </header>

      <main className="site-main" style={{ marginTop: 32, maxWidth: 1200, marginInline: "auto", width: "100%", paddingInline: 20 }}>
        <div className="site-grid">
          <section className="card">
            <div className="card-label">Fleet status</div>
            <div className="card-value ok">{summary.operational}/{summary.total} operational</div>
            <div className="kpi-sub" style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>{summary.needsAttention} machine(s) need attention</div>
          </section>
          <section className="card">
            <div className="card-label">Open issues</div>
            <div className="card-value">{summary.openIssues}</div>
            <div className="kpi-sub" style={{ fontSize: 12, color: "var(--text-muted)", marginTop: 4 }}>Across all fleet units</div>
          </section>
        </div>

        <div className="card-label" style={{ marginTop: 32, marginBottom: 12 }}>Equipment fleet</div>
        <div className="site-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
          {FLEET.map((m) => (
            <section key={m.id} className="card fleet-tile" style={{ padding: 20 }}>
              <div className="fleet-tile-top" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div className="card-label" style={{ marginBottom: 2, fontSize: 13, fontWeight: 600 }}>{m.name}</div>
                  <div className="fleet-type" style={{ fontSize: 12, color: "var(--text-muted)" }}>{m.type}</div>
                </div>
                <div className="fleet-status" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className={`status-dot ${m.status}`} />
                  <span className={`status-text ${m.status}`} style={{ fontSize: 11, fontWeight: 500 }}>{STATUS_LABEL[m.status]}</span>
                </div>
              </div>
              <div style={{ marginTop: 14, fontSize: 12, color: "var(--text-muted)", borderTop: "1px dashed var(--border)", paddingTop: 10 }}>
                <div>Next service: <b>{m.nextMaintenance}</b></div>
                <div style={{ color: m.status === 'critical' ? 'var(--danger)' : 'inherit' }}>{m.nextMaintenanceDue}</div>
              </div>
            </section>
          ))}
        </div>

        <div className="card-label" style={{ marginTop: 48, marginBottom: 12 }}>Manual Library</div>
        <div style={{ background: "#ffffff", borderRadius: 8, border: "1px solid var(--border)", overflow: "hidden" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f5f3ef", textAlign: "left" }}>
                <th style={{ padding: "12px 20px" }}>Document</th>
                <th style={{ padding: "12px 20px" }}>Status</th>
                <th style={{ padding: "12px 20px" }}>Pages</th>
                <th style={{ padding: "12px 20px" }}>Action</th>
                <th style={{ padding: "12px 20px" }}></th>
              </tr>
            </thead>
            <tbody>
              {docs.map((doc) => (
                <tr key={doc.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "14px 20px" }}>{doc.name}</td>
                  <td style={{ padding: "14px 20px" }}><span className={`status-pill status-${doc.status}`}>{doc.status}</span></td>
                  <td style={{ padding: "14px 20px" }}>{doc.pages ?? "—"}</td>
                  <td style={{ padding: "14px 20px" }}>
                    <a href="#" onClick={(e) => handleDownload(e, doc.name)} style={{ fontSize: 12, textDecoration: "none", color: "var(--l-accent)", fontWeight: 500 }}>
                      ⬇ Download
                    </a>
                  </td>
                  <td style={{ padding: "14px 20px", textAlign: "right" }}><button className="admin-btn admin-btn-danger-ghost" onClick={() => handleDeleteDoc(doc.id)}>Delete</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card-label" style={{ marginTop: 48, marginBottom: 12 }}>Team Directory</div>
        <div style={{ background: "#ffffff", borderRadius: 8, border: "1px solid var(--border)", overflow: "hidden" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f5f3ef", textAlign: "left" }}>
                <th style={{ padding: "12px 20px" }}>ID</th>
                <th style={{ padding: "12px 20px" }}>Name</th>
                <th style={{ padding: "12px 20px" }}>Dept</th>
                <th style={{ padding: "12px 20px" }}>Status</th>
                <th style={{ padding: "12px 20px", textAlign: "right" }}></th>
              </tr>
            </thead>
            <tbody>
              {workers.map((w) => (
                <tr key={w.id} style={{ borderBottom: "1px solid var(--border)" }}>
                  <td style={{ padding: "14px 20px" }}>W-{String(w.employee_no).padStart(4, "0")}</td>
                  <td style={{ padding: "14px 20px" }}>{w.name}<br/><span style={{fontSize: 11, color: "var(--text-muted)"}}>{w.email}</span></td>
                  <td style={{ padding: "14px 20px" }}>{w.department || "—"}</td>
                  <td style={{ padding: "14px 20px" }}><span className={`status-pill ${w.must_change_password ? "status-processing" : "status-ready"}`}>{w.must_change_password ? "Pending Login" : "Active"}</span></td>
                  <td style={{ padding: "14px 20px", textAlign: "right" }}><button className="admin-btn admin-btn-danger-ghost" onClick={() => handleDeleteWorker(w.id)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
      
      {/* Dark Footer matching landing page */}
      <footer className="landing-footer" style={{ backgroundColor: "#1c1a17", color: "#e4dfd5", padding: "60px 40px 20px", marginTop: "60px" }}>
        <div className="footer-content" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "40px", maxWidth: "1200px", margin: "0 auto", paddingBottom: "40px" }}>
          <div className="footer-section">
            <div className="footer-brand" style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "20px", fontWeight: 600, color: "#ffffff", marginBottom: "16px" }}>
              <img src="/images/company-logo.png" alt="NexaForge Logo" style={{ width: "28px", height: "28px", objectFit: "contain", filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" }} />
              <span>NexaForge</span>
            </div>
            <p style={{ lineHeight: 1.6, fontSize: 14 }}>
              Precision manufacturing backed by instant digital maintenance insights. 
              Bridging the gap between traditional metalworking and smart floor technology.
            </p>
          </div>
          
          <div className="footer-section">
            <h4 style={{ color: "#ffffff", fontSize: "14px", marginBottom: "16px", fontFamily: "JetBrains Mono, monospace" }}>Quick Links</h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              <li style={{ marginBottom: "12px" }}><Link to="/admin" style={{ color: "#e4dfd5", textDecoration: "none" }}>Admin Console</Link></li>
              <li style={{ marginBottom: "12px" }}><Link to="/dashboard" style={{ color: "#e4dfd5", textDecoration: "none" }}>Worker Fleet Console</Link></li>
              <li style={{ marginBottom: "12px" }}><Link to="/" style={{ color: "#e4dfd5", textDecoration: "none" }}>Main Website</Link></li>
            </ul>
          </div>

          <div className="footer-section">
            <h4 style={{ color: "#ffffff", fontSize: "14px", marginBottom: "16px", fontFamily: "JetBrains Mono, monospace" }}>Contact Us</h4>
            <p style={{ marginBottom: "10px" }}>📍 123 Industrial Parkway</p>
            <p style={{ marginBottom: "10px" }}>📞 (555) 019-2834</p>
            <p style={{ marginBottom: "10px" }}>✉️ operations@nexaforge.com</p>
          </div>
        </div>
        
        <div className="footer-bottom" style={{ textAlign: "center", paddingTop: "24px", borderTop: "1px solid #36322d", fontSize: "12px", maxWidth: "1200px", margin: "0 auto", color: "#9c9284" }}>
          © 2026 NexaForge · Internal Operations & Maintenance Intelligence Platform
        </div>
      </footer>

      <ChatWidget openSignal={chatSignal} />
    </div>
  );
}