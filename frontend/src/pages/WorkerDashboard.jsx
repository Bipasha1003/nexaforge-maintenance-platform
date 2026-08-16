import { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";
import "./LandingPage.css";
import "./Admin.css";
import { API_BASE } from "../config";

const MACHINES_URL = `${API_BASE}/machines`;
const DOCS_URL = `${API_BASE}/documents`;

const STATUS_LABEL = { operational: "Operational", warning: "Needs attention", critical: "Critical" };

function fleetSummary(fleet) {
  const operational = fleet.filter((m) => m.status === "operational").length;
  const needsAttention = fleet.filter((m) => m.status !== "operational").length;
  const openIssues = fleet.reduce((sum, m) => sum + (m.open_issues ?? 0), 0);
  return { total: fleet.length, operational, needsAttention, openIssues };
}

function greetingForHour(hour) {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

const CAPABILITIES = [
  {
    title: "Troubleshoot equipment",
    text: "Ask about an error code or symptom — the assistant searches the manual and cites the exact page it answered from.",
  },
  {
    title: "Check maintenance schedules",
    text: "Ask when a part is due for service — pulled directly from the manual's maintenance-interval sections.",
  },
  {
    title: "Log a new issue",
    text: "Report something you just noticed on the floor. It's recorded for the maintenance team to review.",
  },
  {
    title: "Escalate when unsure",
    text: "If a question is unclear or safety-critical, the assistant hands off to a technician instead of guessing.",
  },
];

export default function WorkerDashboard() {
  const [fleet, setFleet] = useState([]);
  const [docs, setDocs] = useState([]);
  const [docsError, setDocsError] = useState(false);
  const [chatSignal, setChatSignal] = useState(0);
  const [isScrolled, setIsScrolled] = useState(false);
  const navigate = useNavigate();

  const token = localStorage.getItem("worker_token");
  const workerName = localStorage.getItem("worker_name") || "there";
  const firstName = workerName.split(" ")[0];
  const summary = fleetSummary(fleet);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const fetchMachines = useCallback(async () => {
    try {
      const res = await fetch(MACHINES_URL);
      if (res.ok) setFleet(await res.json());
    } catch {
      // silent — polling
    }
  }, []);

  const fetchDocs = useCallback(async () => {
    try {
      const res = await fetch(DOCS_URL);
      if (res.ok) {
        setDocs(await res.json());
        setDocsError(false);
      } else {
        setDocsError(true);
      }
    } catch {
      setDocsError(true);
    }
  }, []);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchMachines();
    fetchDocs();
    const interval = setInterval(() => {
      fetchMachines();
      fetchDocs();
    }, 5000);
    return () => clearInterval(interval);
  }, [token, navigate, fetchMachines, fetchDocs]);

  function handleLogout() {
    localStorage.removeItem("worker_token");
    localStorage.removeItem("worker_name");
    localStorage.removeItem("worker_username");
    navigate("/");
  }

  const handleDownload = (docId, docName) => {
    const identifier = docId || docName;
    if (!identifier) {
      alert("Error: Document identifier missing.");
      return;
    }
    
    const downloadUrl = `${API_BASE}/documents/${encodeURIComponent(identifier)}/download`;
    
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.setAttribute("download", docName || "document.pdf");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const heroLine = useMemo(() => {
    if (summary.total === 0) {
      return "No machines on the floor yet — check back once the admin team adds equipment.";
    }
    if (summary.needsAttention === 0) {
      return `All ${summary.total} machines are running clean. Ask the assistant if anything looks off.`;
    }
    return `${summary.operational} of ${summary.total} machines are running clean. ${summary.openIssues === 1 ? "One open issue is" : `${summary.openIssues} open issues are`} logged on the floor.`;
  }, [summary]);

  return (
    <div className="site site-bg-worker">
      <header className={`landing-header ${isScrolled ? "scrolled" : ""}`} style={{ position: "sticky", top: 0, zIndex: 1000, background: "rgba(255, 255, 255, 0.95)", backdropFilter: "blur(8px)", borderBottom: "1px solid #eaeaea" }}>
        <div className="landing-brand" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
          <img
            src="/images/company-logo.png"
            alt="NexaForge Logo"
            style={{ width: "38px", height: "38px", objectFit: "contain", filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" }}
          />
          <div>
            <div className="landing-brand-title">NexaForge</div>
            <div className="landing-brand-subtitle" style={{ color: "#6b6459" }}>Fleet Console</div>
          </div>
        </div>

        <div className="landing-header-actions admin-header-actions-row">
          <a href="#equipment-fleet" className="admin-text-btn" style={{ color: "var(--text)", fontWeight: 500 }}>Overview</a>
          <a href="#capabilities" className="admin-text-btn" style={{ color: "var(--text)", fontWeight: 500 }}>Capabilities</a>
          <a href="#documents" className="admin-text-btn" style={{ color: "var(--text)", fontWeight: 500 }}>Documents</a>
          <a href="#maintenance-log" className="admin-text-btn" style={{ color: "var(--text)", fontWeight: 500 }}>Maintenance log</a>

          <button className="admin-ai-btn" onClick={() => setChatSignal((n) => n + 1)}>
            Ask assistant
          </button>

          <Link to="/profile" className="admin-text-btn" style={{ color: "var(--text)", fontWeight: 500, textDecoration: "none" }}>
            My profile
          </Link>

          <span className="admin-user-name">
            {firstName}
          </span>

          <button className="admin-logout-btn" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="site-main" style={{ marginTop: 36, maxWidth: 1240, marginInline: "auto", width: "100%", paddingInline: 24 }}>

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
            Fleet overview
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
            <div className="card-label" style={{ fontSize: 15 }}>Open issues (all machines)</div>
            <div className="card-value" style={{ fontSize: 30, marginTop: 6 }}>{summary.openIssues}</div>
            <div className="kpi-sub" style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 6 }}>See maintenance log below</div>
          </section>
          <section className="card" style={{ padding: 26, borderRadius: 14 }}>
            <div className="card-label" style={{ fontSize: 15 }}>Manuals ingested</div>
            <div className="card-value" style={{ fontSize: 30, marginTop: 6 }}>
              {docsError ? "—" : `${docs.filter((d) => d.status?.toLowerCase() === "ready").length}/${docs.length || 0}`}
            </div>
            <div className="kpi-sub" style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 6 }}>Assistant covers all ingested manuals</div>
          </section>
        </div>

        <div id="equipment-fleet" style={{ marginTop: 40, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Equipment fleet</div>
        </div>

        <div className="site-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(270px, 1fr))", gap: 20 }}>
          {fleet.length === 0 && (
            <div className="card" style={{ padding: 26, borderRadius: 14, color: "var(--text-muted)", gridColumn: "1 / -1", textAlign: "center" }}>
              No machines on the floor yet.
            </div>
          )}
          {fleet.map((m) => (
            <section key={m.id} className="card fleet-tile" style={{ padding: 26, borderRadius: 14, minHeight: 190 }}>
              <div className="fleet-tile-top" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div>
                  <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 11.5, color: "var(--text-muted)", letterSpacing: "0.04em" }}>
                    {m.id.split("-")[0].toUpperCase()}
                  </div>
                  <div className="card-label" style={{ marginTop: 2, fontSize: 16, fontWeight: 700, color: "var(--text)" }}>{m.name}</div>
                </div>
                <div className="fleet-status" style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <span className={`status-dot ${m.status}`} />
                  <span className={`status-text ${m.status}`} style={{ fontSize: 13, fontWeight: 600 }}>{STATUS_LABEL[m.status]}</span>
                </div>
              </div>

              <div style={{ marginTop: 16, fontSize: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)", marginBottom: 8 }}>
                  <span>Last check-in</span>
                  <span>{m.last_check_in}</span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                  <span style={{ color: "var(--text-muted)" }}>Next maintenance</span>
                  <span style={{ textAlign: "right", fontWeight: 600, color: "var(--text)" }}>
                    {m.next_maintenance}
                    <div style={{ fontStyle: "italic", fontWeight: 400, color: m.status === "critical" ? "var(--danger)" : "var(--text-muted)", fontSize: 12.5 }}>
                      {m.next_maintenance_due}
                    </div>
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", color: "var(--text-muted)" }}>
                  <span>Open issues</span>
                  <span style={{ fontWeight: 600, color: "var(--text)" }}>{m.open_issues ?? 0}</span>
                </div>
              </div>

              <div
                style={{
                  marginTop: 16,
                  padding: "8px 12px",
                  borderRadius: 8,
                  fontSize: 12.5,
                  fontFamily: '"JetBrains Mono", monospace',
                  background: m.status === "critical" ? "rgba(194, 59, 59, 0.08)" : "rgba(47, 125, 79, 0.08)",
                  color: m.status === "critical" ? "var(--danger)" : "var(--success)",
                }}
              >
                Manual ingested — assistant available below
              </div>
            </section>
          ))}
        </div>

        <div id="capabilities" style={{ marginTop: 56, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>What the assistant can do</div>
        </div>
        <div style={{ background: "rgba(255,255,255,0.95)", border: "1px solid var(--border)", borderRadius: 14, padding: 32 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            {CAPABILITIES.map((c) => (
              <div key={c.title} className="card" style={{ padding: 20, borderRadius: 10 }}>
                <div style={{ fontFamily: '"Fraunces", serif', fontWeight: 600, fontSize: 16, color: "var(--l-accent)", marginBottom: 8 }}>{c.title}</div>
                <p style={{ fontSize: 14, lineHeight: 1.6, color: "var(--text-muted)", margin: 0 }}>{c.text}</p>
              </div>
            ))}
          </div>
        </div>

        <div id="documents" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 56, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Ingested Documents</div>
        </div>
        
        {/* --- MOBILE TABLE SCROLL FIX ADDED HERE --- */}
        <div className="table-wrapper" style={{ background: "#ffffff", borderRadius: 14, border: "1px solid var(--border)", overflowX: "auto", boxShadow: "0 12px 28px rgba(28, 26, 23, 0.08)" }}>
          <table className="admin-table" style={{ width: "100%", borderCollapse: "collapse", fontSize: 15 }}>
            <thead>
              <tr style={{ background: "#f5f3ef", textAlign: "left" }}>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Document</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Status</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Pages</th>
                <th style={{ padding: "16px 24px", fontSize: 13 }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {docsError ? (
                <tr>
                  <td colSpan={4} style={{ padding: "20px 24px", color: "var(--danger)", fontStyle: "italic", textAlign: "center" }}>
                    Failed to load documents. Check backend connection.
                  </td>
                </tr>
              ) : docs.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ padding: "20px 24px", color: "var(--text-muted)", fontStyle: "italic", textAlign: "center" }}>
                    No documents have been ingested yet.
                  </td>
                </tr>
              ) : (
                docs.map((doc) => (
                  <tr key={doc.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "18px 24px", fontWeight: 500 }}>{doc.name}</td>
                    <td style={{ padding: "18px 24px" }}><span className={`status-pill status-${doc.status?.toLowerCase() || 'processing'}`} style={{ fontSize: 12.5, padding: "4px 12px" }}>{doc.status}</span></td>
                    <td style={{ padding: "18px 24px" }}>{doc.pages ?? "—"}</td>
                    <td style={{ padding: "18px 24px" }}>
                      <a href="#" onClick={(e) => { e.preventDefault(); handleDownload(doc.id || doc.name, doc.name); }} style={{ fontSize: 14, textDecoration: "none", color: "var(--l-accent)", fontWeight: 600, cursor: "pointer" }}>
                        ⬇ Download
                      </a>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div id="maintenance-log" style={{ marginTop: 56, marginBottom: 16 }}>
          <div className="card-label" style={{ fontSize: 20, fontFamily: '"Fraunces", serif', fontWeight: 600, color: "var(--text)" }}>Maintenance Log</div>
        </div>
        <div style={{ background: "rgba(255,255,255,0.95)", border: "1px solid var(--border)", borderRadius: 14, padding: 32 }}>
          <div
            style={{
              fontFamily: '"JetBrains Mono", monospace',
              fontSize: 12,
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              color: "var(--text-muted)",
              marginBottom: 14,
            }}
          >
            Maintenance log — sample entry
          </div>
          <div className="card" style={{ padding: 20, borderRadius: 10 }}>
            <p style={{ fontSize: 14.5, lineHeight: 1.7, color: "var(--text-muted)", margin: 0 }}>
              Example incident pulled from the ingested manual: technician R. Alvarez logged E-322 caused by chip
              sludge buildup from a missed weekly strainer cleaning; resolved by cleaning the strainer, flushing
              the line, and a pump reset. Ask the assistant for any other logged incident by error code or date.
            </p>
          </div>
          <p style={{ fontSize: 12.5, color: "var(--text-muted)", marginTop: 14, marginBottom: 0, fontStyle: "italic" }}>
            This section is a placeholder — log_issue() in agent/actions.py currently only prints to console, so
            real entries aren't stored anywhere yet.
          </p>
        </div>
      </main>

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
              <li style={{ marginBottom: "14px" }}><Link to="/dashboard" style={{ color: "#e4dfd5", textDecoration: "none" }}>Fleet Console</Link></li>
              <li style={{ marginBottom: "14px" }}><Link to="/admin" style={{ color: "#e4dfd5", textDecoration: "none" }}>Admin Panel</Link></li>
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

      <ChatWidget openSignal={chatSignal} />
    </div>
  );
}